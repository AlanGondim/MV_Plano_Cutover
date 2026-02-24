import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from graphviz import Digraph
import io

# Configuração da página para Dashboard Executivo
st.set_page_config(page_title="Gestão de Cutover Integrado Prime", layout="wide")

# --- 1. BASE DE DADOS INTEGRAL (165 TAREFAS) ---
if 'tasks_df' not in st.session_state:
    # Estrutura baseada na volumetria solicitada
    tasks = []
    
    # VERTICAL HOSPITALAR (60 Tarefas)
    for i in range(1, 61):
        tasks.append({
            "ID": f"H{i}", "Vertical": "Hospitalar", "Responsabilidade": "MV" if i < 10 else "Cliente",
            "Tarefa": f"Tarefa Hospitalar {i}: Processo de Cutover", "Predecessora": f"H{i-1}" if i > 1 else "0",
            "Duração": 2 if i % 5 == 0 else 1, "Responsável": "Equipe Hospitalar", "Status": "Pendente"
        })
        
    # VERTICAL FLOWTI (34 Tarefas)
    for i in range(1, 35):
        tasks.append({
            "ID": f"F{i}", "Vertical": "FLOWTI", "Responsabilidade": "MV",
            "Tarefa": f"Infraestrutura FLOWTI {i}: Configuração Técnica", "Predecessora": f"F{i-1}" if i > 1 else "H1",
            "Duração": 1, "Responsável": "Equipe Infra", "Status": "Pendente"
        })

    # VERTICAL MEDICINA DIAGNÓSTICA (39 Tarefas)
    for i in range(1, 40):
        tasks.append({
            "ID": f"D{i}", "Vertical": "Medicina Diagnóstica", "Responsabilidade": "Cliente",
            "Tarefa": f"SADT/Diagnóstico {i}: Validação e Carga", "Predecessora": f"D{i-1}" if i > 1 else "H1",
            "Duração": 1, "Responsável": "Equipe Médica", "Status": "Pendente"
        })

    # VERTICAL PLANO DE SAÚDE (32 Tarefas)
    for i in range(1, 33):
        tasks.append({
            "ID": f"P{i}", "Vertical": "Plano de Saúde", "Responsabilidade": "MV",
            "Tarefa": f"Operadora {i}: Carga de Beneficiários e Regras", "Predecessora": f"P{i-1}" if i > 1 else "H1",
            "Duração": 2, "Responsável": "Equipe Operadora", "Status": "Pendente"
        })

    st.session_state.tasks_df = pd.DataFrame(tasks)

# --- 2. MOTOR DE CÁLCULO CPM ---
def calculate_schedule(df, start_date, tolerance):
    df = df.copy()
    df['Duração'] = pd.to_numeric(df['Duração']).fillna(1)
    df['Data Início'] = pd.NaT
    df['Data Término'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    end_dates = {}
    for index, row in df.iterrows():
        t_id, pred_id = str(row['ID']), str(row['Predecessora'])
        duration = int(row['Duração'])
        
        current_start = end_dates.get(pred_id, start_date)
        current_end = current_start + timedelta(days=duration)
        
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Término'] = current_end
        df.at[index, 'Data Limite'] = current_end + timedelta(days=tolerance)
        end_dates[t_id] = current_end
    return df

# --- 3. INTERFACE ---
st.title("🚀 Dashboard de Cutover Integrado Prime (165 Atividades)")

with st.sidebar:
    st.header("⚙️ Gestão do Programa")
    verticais_ativadas = st.multiselect("Selecione as Verticais do Escopo", 
                                        ["Hospitalar", "FLOWTI", "Medicina Diagnóstica", "Plano de Saúde"],
                                        default=["Hospitalar", "FLOWTI", "Medicina Diagnóstica", "Plano de Saúde"])
    
    dt_inicio = st.date_input("Data de Início do Programa", datetime.now())
    desvio = st.number_input("Tolerância de Segurança (Dias)", min_value=0, value=3)

    st.divider()
    st.subheader("🛠️ Editar Atividade Selecionada")
    sel_id = st.selectbox("Selecione o ID para edição", st.session_state.tasks_df['ID'].unique())
    idx = st.session_state.tasks_df[st.session_state.tasks_df['ID'] == sel_id].index[0]
    
    with st.expander("Campos de Edição"):
        new_dur = st.number_input("Duração", value=int(st.session_state.tasks_df.at[idx, 'Duração']))
        new_stat = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluído"], 
                                index=["Pendente", "Em Andamento", "Concluído"].index(st.session_state.tasks_df.at[idx, 'Status']))
        new_pred = st.text_input("Predecessora", value=st.session_state.tasks_df.at[idx, 'Predecessora'])
        
        if st.button("💾 Salvar Alterações"):
            st.session_state.tasks_df.at[idx, 'Duração'] = new_dur
            st.session_state.tasks_df.at[idx, 'Status'] = new_stat
            st.session_state.tasks_df.at[idx, 'Predecessora'] = new_pred
            st.rerun()

# --- 4. DASHBOARD E GRÁFICOS ---
df_calc = calculate_schedule(st.session_state.tasks_df, datetime.combine(dt_inicio, datetime.min.time()), desvio)
df_final = df_calc[df_calc['Vertical'].isin(verticais_ativadas)]

tab1, tab2, tab3 = st.tabs(["📋 Planilha Geral", "📅 Gráfico de GANTT", "🕸️ Diagrama PERT"])

with tab1:
    st.subheader("Controle Executivo de Tarefas")
    # Formatação para exibição
    df_disp = df_final.copy()
    for c in ['Data Início', 'Data Término', 'Data Limite']: df_disp[c] = df_disp[c].dt.strftime('%d/%m/%Y')
    st.dataframe(df_disp, use_container_width=True, hide_index=True)
    
    # EXPORTAÇÃO EXCEL
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_disp.to_excel(writer, index=False, sheet_name='Cronograma_Cutover')
    st.download_button("📥 Baixar Cronograma em Excel", data=buffer.getvalue(), file_name="Plano_Integrado_Prime.xlsx")

with tab2:
    st.subheader("Caminho Crítico do Programa")
        fig = px.timeline(df_final, x_start="Data Início", x_end="Data Término", y="Tarefa", color="Vertical",
                      hover_data=["ID", "Responsável", "Data Limite"])
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Rede de Dependências Integrada")
        dot = Digraph(comment='PERT', graph_attr={'rankdir':'LR', 'size': '10,10'})
    # Amostra das primeiras 20 para não sobrecarregar visualmente
    for _, row in df_final.head(30).iterrows():
        dot.node(row['ID'], f"{row['ID']}\n{row['Tarefa'][:20]}...")
        if row['Predecessora'] != '0': dot.edge(row['Predecessora'], row['ID'])
    st.graphviz_chart(dot)
