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
    tasks = []
    # Hospitalar: 60 tarefas 
    for i in range(1, 61):
        tasks.append({"ID": f"H{i}", "Vertical": "Hospitalar", "Tarefa": f"Atividade Hospitalar {i}", "Predecessora": f"H{i-1}" if i > 1 else "0", "Duração": 1, "Status": "Pendente"})
    # FLOWTI: 34 tarefas 
    for i in range(1, 35):
        tasks.append({"ID": f"F{i}", "Vertical": "FLOWTI", "Tarefa": f"Infra FLOWTI {i}", "Predecessora": f"F{i-1}" if i > 1 else "H1", "Duração": 1, "Status": "Pendente"})
    # Medicina Diagnóstica: 39 tarefas 
    for i in range(1, 40):
        tasks.append({"ID": f"D{i}", "Vertical": "Medicina Diagnóstica", "Tarefa": f"SADT {i}", "Predecessora": f"D{i-1}" if i > 1 else "H1", "Duração": 1, "Status": "Pendente"})
    # Plano de Saúde: 32 tarefas 
    for i in range(1, 33):
        tasks.append({"ID": f"P{i}", "Vertical": "Plano de Saúde", "Tarefa": f"Operadora {i}", "Predecessora": f"P{i-1}" if i > 1 else "H1", "Duração": 1, "Status": "Pendente"})
    
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

# --- 3. INTERFACE E DASHBOARD ---
st.title("🚀 Painel Cutover Integrado Prime")

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
        st.success(f"Status de {v_massa} atualizado para {s_massa}!")
        st.rerun()

# --- 4. INDICADORES E VISUALIZAÇÕES ---
df_calc = calculate_schedule(st.session_state.tasks_df, datetime.combine(dt_inicio, datetime.min.time()), desvio)
df_final = df_calc[df_calc['Vertical'].isin(v_ativadas)]

# Painel de Progresso
st.subheader("📈 Progresso por Vertical")
cols = st.columns(len(v_ativadas))
for i, v in enumerate(v_ativadas):
    v_tasks = df_final[df_final['Vertical'] == v]
    perc = (len(v_tasks[v_tasks['Status'] == 'Concluído']) / len(v_tasks) * 100) if len(v_tasks) > 0 else 0
    cols[i].metric(v, f"{perc:.1f}%")

tab1, tab2, tab3 = st.tabs(["📋 Planilha", "📅 Gantt", "🕸️ PERT"])

with tab1:
    df_disp = df_final.copy()
    for c in ['Data Início', 'Data Término', 'Data Limite']: df_disp[c] = df_disp[c].dt.strftime('%d/%m/%Y')
    st.dataframe(df_disp, use_container_width=True, hide_index=True)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_disp.to_excel(writer, index=False, sheet_name='Cutover')
    st.download_button("📥 Baixar Excel", data=buffer.getvalue(), file_name="Plano_Integrado.xlsx")

with tab2:
    
    fig = px.timeline(df_final, x_start="Data Início", x_end="Data Término", y="Tarefa", color="Vertical")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    
    dot = Digraph(comment='PERT', graph_attr={'rankdir':'LR'})
    for _, row in df_final.head(30).iterrows():
        dot.node(row['ID'], f"{row['ID']}\n{row['Tarefa'][:15]}...")
        if row['Predecessora'] != '0' and row['Predecessora'] in df_final['ID'].values:
            dot.edge(row['Predecessora'], row['ID'])
    st.graphviz_chart(dot)
