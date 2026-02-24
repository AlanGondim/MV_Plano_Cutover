import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from graphviz import Digraph
import io

# Configuração da página para Dashboard Executivo
st.set_page_config(page_title="Cutover Integrado Prime 100%", layout="wide")

# --- 1. BASE DE DADOS INTEGRAL (165 TAREFAS) ---
if 'tasks_df' not in st.session_state:
    # Carregando as tarefas do CSV gerado com o escopo completo
    st.session_state.tasks_df = pd.read_csv('plano_cutover_integrado_165.csv')

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

# --- 3. INTERFACE E DASHBOARD ---
st.title("🚀 Dashboard de Cutover Integrado Prime (165 Atividades)")

with st.sidebar:
    st.header("⚙️ Gestão Estratégica")
    verticais_list = ["Hospitalar", "FLOWTI", "Medicina Diagnóstica", "Plano de Saúde"]
    v_ativadas = st.multiselect("Verticais no Escopo", verticais_list, default=verticais_list)
    dt_inicio = st.date_input("Início do Programa", datetime.now())
    desvio = st.number_input("Tolerância (Dias)", min_value=0, value=3)

    st.divider()
    st.header("⚡ Atualização em Massa")
    v_massa = st.selectbox("Selecionar Vertical", verticais_list)
    s_massa = st.selectbox("Novo Status", ["Pendente", "Em Andamento", "Concluído"])
    if st.button("🚀 Aplicar em Massa"):
        st.session_state.tasks_df.loc[st.session_state.tasks_df['Vertical'] == v_massa, 'Status'] = s_massa
        st.rerun()

    st.divider()
    st.header("🛠️ Gerenciar Tarefas")
    with st.expander("✏️ Editar/Excluir"):
        sel_id = st.selectbox("Selecione o ID", st.session_state.tasks_df['ID'].astype(str).unique())
        idx = st.session_state.tasks_df[st.session_state.tasks_df['ID'].astype(str) == sel_id].index[0]
        if st.button("Remover Tarefa"):
            st.session_state.tasks_df = st.session_state.tasks_df.drop(idx).reset_index(drop=True)
            st.rerun()

# --- 4. INDICADORES E ALERTAS ---
df_calc = calculate_schedule(st.session_state.tasks_df, datetime.combine(dt_inicio, datetime.min.time()), desvio)
df_final = df_calc[df_calc['Vertical'].isin(v_ativadas)]

# Painel de Progresso Superior
st.subheader("📈 Progresso Real por Vertical")
cols = st.columns(len(v_ativadas))
for i, v in enumerate(v_ativadas):
    v_tasks = df_final[df_final['Vertical'] == v]
    perc = (len(v_tasks[v_tasks['Status'] == 'Concluído']) / len(v_tasks) * 100) if len(v_tasks) > 0 else 0
    cols[i].metric(v, f"{perc:.1f}%")

tab1, tab2, tab3 = st.tabs(["📋 Planilha de Controle", "📅 Gráfico de GANTT", "🕸️ Diagrama PERT (Rede)"])

with tab1:
    st.subheader("Controle Detalhado e Alertas de Atraso")
    # Alerta visual: Data Limite ultrapassada e não concluída
    def highlight_delay(row):
        if row['Status'] != 'Concluído' and row['Data Limite'] < datetime.now():
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)
    
    df_disp = df_final.copy()
    st.dataframe(df_disp.style.apply(highlight_delay, axis=1), use_container_width=True, hide_index=True)
    
    # Exportação
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_disp.to_excel(writer, index=False, sheet_name='Cutover')
    st.download_button("📥 Baixar Excel Completo", data=buffer.getvalue(), file_name="Plano_Integrado_100.xlsx")

with tab2:
    fig = px.timeline(df_final, x_start="Data Início", x_end="Data Término", y="Tarefa", color="Status",
                      color_discrete_map={"Concluído": "green", "Em Andamento": "orange", "Pendente": "red"})
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Rede de Dependências (PERT)")
    v_pert = st.selectbox("Filtrar PERT por Vertical para Melhor Visualização", ["Todas"] + verticais_list)
    df_pert = df_final if v_pert == "Todas" else df_final[df_final['Vertical'] == v_pert]
    
    # Melhoria de Tamanho: Definindo atributos de gráfico maiores
    dot = Digraph(comment='PERT', graph_attr={'rankdir':'LR', 'size': '30,30!', 'ratio': 'fill', 'nodesep': '0.5', 'ranksep': '1.0'})
    
    # Adicionando nós e arestas de forma legível
    for _, row in df_pert.iterrows():
        color = 'green' if row['Status'] == 'Concluído' else 'orange' if row['Status'] == 'Em Andamento' else 'black'
        shape = 'box' if row['Vertical'] == 'Hospitalar' else 'ellipse'
        dot.node(str(row['ID']), f"ID: {row['ID']}\n{row['Tarefa'][:30]}...", color=color, shape=shape, penwidth='2')
        
        if str(row['Predecessora']) != '0' and str(row['Predecessora']) in df_pert['ID'].astype(str).values:
            dot.edge(str(row['Predecessora']), str(row['ID']), color='gray', penwidth='1')
            
    st.graphviz_chart(dot, use_container_width=True)
