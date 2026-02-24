import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
from datetime import datetime, timedelta
from graphviz import Digraph
import io

# Configuração da página
st.set_page_config(page_title="Cutover Prime MV - Gestão Integrada", layout="wide")

# --- 1. INICIALIZAÇÃO E DADOS ---
if 'tasks_df' not in st.session_state:
    # Dados base baseados no histórico e no documento (Amostra das 60 primeiras)
    initial_tasks = [
        {"ID": "1", "Vertical": "Hospitalar", "Responsabilidade": "MV", "Descrição": "Verificar verticais envolvidas no projeto", "Predecessora": "0", "Duração": 0, "Responsável": "Equipe MV", "Status": "Concluído"},
        {"ID": "2", "Vertical": "Hospitalar", "Responsabilidade": "MV", "Descrição": "Verificar triggers, procedanse e functions próprias", "Predecessora": "1", "Duração": 2, "Responsável": "DBA MV", "Status": "Concluído"},
        {"ID": "3", "Vertical": "Hospitalar", "Responsabilidade": "Cliente", "Descrição": "Atualizar a versão do sistema", "Predecessora": "2", "Duração": 2, "Responsável": "TI Local", "Status": "Em Andamento"},
        {"ID": "4", "Vertical": "Hospitalar", "Responsabilidade": "Cliente", "Descrição": "Atualizar a base de CEP", "Predecessora": "3", "Duração": 2, "Responsável": "TI Local", "Status": "Pendente"},
        {"ID": "18", "Vertical": "Hospitalar", "Responsabilidade": "Cliente", "Descrição": "Migrar relatórios para Report Designer", "Predecessora": "17", "Duração": 45, "Responsável": "TI Local", "Status": "Pendente"},
        {"ID": "50", "Vertical": "Hospitalar", "Responsabilidade": "Cliente", "Descrição": "Refazer documentos em OCX no Editor", "Predecessora": "49", "Duração": 45, "Responsável": "TI Local", "Status": "Pendente"},
        # Adicione aqui as demais tarefas até 152 ou importe via CSV
    ]
    st.session_state.tasks_df = pd.DataFrame(initial_tasks)

# --- 2. MOTOR DE CÁLCULO CPM (CAMINHO CRÍTICO) ---
def calculate_cpm(df, start_date, tolerance):
    df = df.copy()
    df['Duração'] = pd.to_numeric(df['Duração']).fillna(0)
    
    # Forward Pass
    tasks = {}
    for _, row in df.iterrows():
        tasks[row['ID']] = {
            'dur': row['Duração'],
            'preds': [p.strip() for p in str(row['Predecessora']).split(',') if p.strip() != '0' and p.strip() != ''],
            'es': 0, 'ef': 0, 'ls': 0, 'lf': 0
        }

    # Early Start & Early Finish
    for t_id in tasks:
        def get_es(tid):
            if not tasks[tid]['preds']: return 0
            return max([get_ef(p) for p in tasks[tid]['preds'] if p in tasks])
        def get_ef(tid):
            tasks[tid]['es'] = get_es(tid)
            tasks[tid]['ef'] = tasks[tid]['es'] + tasks[tid]['dur']
            return tasks[tid]['ef']
        get_ef(t_id)

    # Backward Pass
    max_ef = max([t['ef'] for t in tasks.values()]) if tasks else 0
    for t_id in reversed(list(tasks.keys())):
        tasks[t_id]['lf'] = max_ef
        tasks[t_id]['ls'] = max_ef - tasks[t_id]['dur']

    # Cálculo final de datas
    for index, row in df.iterrows():
        t_id = row['ID']
        es_days = tasks[t_id]['es']
        ef_days = tasks[t_id]['ef']
        
        df.at[index, 'Data Início'] = start_date + timedelta(days=es_days)
        df.at[index, 'Data Término'] = start_date + timedelta(days=ef_days)
        # Data Limite = Término + Tolerância
        df.at[index, 'Data Limite'] = start_date + timedelta(days=ef_days + tolerance)
        df.at[index, 'Slack'] = tasks[t_id]['lf'] - tasks[t_id]['ef']
        df.at[index, 'Is_Critical'] = df.at[index, 'Slack'] <= 0

    return df

# --- 3. INTERFACE E CRUD ---
st.title("📊 Painel Cutover Integrado Prime")

with st.sidebar:
    st.header("⚙️ Configurações e CRUD")
    data_projeto = st.date_input("Data de Início do Projeto", datetime.now())
    tolerancia = st.number_input("Tolerância (Dias)", min_value=0, value=3)
    verticais_proj = st.multiselect("Verticais do Programa", 
                                    ["Hospitalar", "Medicina Diagnóstica", "FLOWTI", "Plano de Saúde"],
                                    default=["Hospitalar"])
    
    st.divider()
    st.subheader("🆕 Adicionar Tarefa")
    with st.form("new_task"):
        n_id = st.text_input("ID")
        n_desc = st.text_input("Descrição")
        n_dur = st.number_input("Duração", min_value=0)
        n_pred = st.text_input("Predecessoras (IDs separados por vírgula)")
        n_resp = st.text_input("Responsável")
        n_vert = st.selectbox("Vertical", ["Hospitalar", "Medicina Diagnóstica", "FLOWTI", "Plano de Saúde"])
        n_status = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluído"])
        if st.form_submit_button("Adicionar"):
            new_row = {"ID": n_id, "Vertical": n_vert, "Responsabilidade": "Definir", "Descrição": n_desc, 
                       "Predecessora": n_pred, "Duração": n_dur, "Responsável": n_resp, "Status": n_status}
            st.session_state.tasks_df = pd.concat([st.session_state.tasks_df, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

# Processamento
df_calc = calculate_cpm(st.session_state.tasks_df, data_projeto, tolerancia)
df_filtered = df_calc[df_calc['Vertical'].isin(verticais_proj)]

# --- 4. VISUALIZAÇÕES ---
tab1, tab2, tab3 = st.tabs(["📋 Planilha de Controle", "📅 Gráfico de GANTT", "🕸️ Diagrama PERT"])

with tab1:
    st.subheader("Edição Direta da Base de Dados")
    edited_df = st.data_editor(df_filtered, num_rows="dynamic", use_container_width=True, hide_index=True,
                               key="data_editor")
    if st.button("💾 Salvar Alterações da Tabela"):
        st.session_state.tasks_df = edited_df
        st.rerun()

with tab2:
    st.subheader("Cronograma Visual")
    if not df_filtered.empty:
        fig = px.timeline(df_filtered, x_start="Data Início", x_end="Data Término", y="Descrição", color="Is_Critical",
                          hover_data=["ID", "Responsável", "Status", "Data Limite"],
                          color_discrete_map={True: 'red', False: 'blue'},
                          title="Caminho Crítico em Vermelho")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Rede de Predependências (Caminho Crítico)")
    dot = Digraph(comment='PERT Chart', graph_attr={'rankdir':'LR'})
    for _, row in df_filtered.iterrows():
        color = 'red' if row['Is_Critical'] else 'black'
        label = f"{row['ID']}\n{row['Descrição']}\nDur: {row['Duração']}d"
        dot.node(row['ID'], label, color=color, fontcolor=color)
        
        preds = [p.strip() for p in str(row['Predecessora']).split(',') if p.strip() != '0' and p.strip() != '']
        for p in preds:
            if p in df_filtered['ID'].values:
                dot.edge(p, row['ID'], color=color)
    st.graphviz_chart(dot)

# Exportação
st.divider()
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_calc.to_excel(writer, index=False, sheet_name='Plano_Cutover')
st.download_button("📥 Exportar para Excel", data=buffer.getvalue(), file_name="Plano_Cutover_Integrado.xlsx")
