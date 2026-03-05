import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Smart Cutover AI", layout="wide", initial_sidebar_state="expanded")

# CSS para dar um ar moderno e "tech"
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .ai-audit-card { padding: 20px; border-radius: 10px; border-left: 5px solid #7000ff; background-color: #f0e6ff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NEGÓCIO ---

def calculate_schedule(df, project_start_date):
    if df.empty: return df
    df = df.copy()
    df['Duração (Dias)'] = pd.to_numeric(df['Duração (Dias)'], errors='coerce').fillna(1)
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    
    end_dates = {}
    project_start_dt = datetime.combine(project_start_date, datetime.min.time())

    for index, row in df.iterrows():
        task_id = str(row['ID'])
        pred_id = str(row['Predecessora']).strip()
        duration = int(row['Duração (Dias)'])
        
        if pred_id in ['0', '', 'None', task_id] or pred_id not in end_dates:
            current_start = project_start_dt
        else:
            current_start = end_dates[pred_id]
        
        current_end = current_start + timedelta(days=duration)
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Fim'] = current_end
        end_dates[task_id] = current_end
        
    return df

# --- ESTADO DA SESSÃO (MEMÓRIA DO APP) ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame([
        {"ID": "1", "Vertical": "Infra", "Tarefa": "Setup de Servidores", "Predecessora": "0", "Duração (Dias)": 2, "Status": "Concluído", "Criticidade": "Alta"},
        {"ID": "2", "Vertical": "Dados", "Tarefa": "Migração de Banco", "Predecessora": "1", "Duração (Dias)": 3, "Status": "Em andamento", "Criticidade": "Crítica"},
        {"ID": "3", "Vertical": "Apps", "Tarefa": "Deploy de APIs", "Predecessora": "2", "Duração (Dias)": 1, "Status": "Pendente", "Criticidade": "Média"},
    ])

# --- SIDEBAR - CONTROLES ---
with st.sidebar:
    st.title("🚀 Smart Cutover")
    st.subheader("Configurações do Programa")
    data_base = st.date_input("Início do Cutover", datetime.now(), format="DD/MM/YYYY")
    
    st.divider()
    st.markdown("### 🤖 Configurações de IA")
    model_sensitivity = st.slider("Sensibilidade do Auditor IA", 0, 100, 75)
    st.info("A IA está varrendo logs de testes e sentimentos em tempo real.")

# --- CORPO PRINCIPAL ---
col_t, col_ai = st.columns([0.7, 0.3])

with col_t:
    st.subheader("📅 Cronograma Interativo")
    st.caption("Edite, adicione ou exclua linhas diretamente na tabela abaixo.")
    
    # EDITORA DE DADOS (A Inovação na Gestão)
    edited_df = st.data_editor(
        st.session_state.tasks,
        num_rows="dynamic", # PERMITE INCLUIR E EXCLUIR LINHAS
        use_container_width=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(options=["Pendente", "Em andamento", "Concluído", "Atrasado"]),
            "Vertical": st.column_config.SelectboxColumn(options=["Infra", "Dados", "Apps", "Negócio", "QA"]),
            "Criticidade": st.column_config.SelectboxColumn(options=["Baixa", "Média", "Alta", "Crítica"]),
        },
        key="data_editor"
    )
    st.session_state.tasks = edited_df

    # Processamento do Cronograma
    df_final = calculate_schedule(edited_df, data_base)

with col_ai:
    st.subheader("🧠 Auditoria Final IA")
    
    # Simulação de Análise Preditiva (Inovação mencionada no texto)
    prob_sucesso = random.randint(60, 95)
    color = "green" if prob_sucesso > 85 else "orange" if prob_sucesso > 75 else "red"
    
    st.markdown(f"""
    <div class="ai-audit-card">
        <h4>Probabilidade de Sucesso</h4>
        <h2 style="color:{color};">{prob_sucesso}%</h2>
        <small>Baseado em 142 artefatos e 12 verticais</small>
    </div>
    """, unsafe_allow_html=True)

    # Insights Gerados por NLP e Análise Predutiva
    st.markdown("##### 🚩 Sinais de Alerta (Preventivo)")
    if prob_sucesso < 90:
        st.warning("**Risco de QA:** O módulo 'Dados' teve 20% menos testes que o padrão histórico.")
        st.error("**Engajamento:** Sentiment Analysis indica ansiedade alta na Vertical de Negócio.")
    else:
        st.success("Checklists de corte validados com 100% de aderência.")

# --- VISUALIZAÇÃO GANTT ---
st.divider()
if not df_final.empty:
    fig = px.timeline(
        df_final, 
        x_start="Data Início", 
        x_end="Data Fim", 
        y="Tarefa", 
        color="Vertical",
        hover_data=["Status", "Criticidade"],
        title="Visualização do Fluxo de Virada (Gantt Dinâmico)",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- MÉTRICAS DE PROGRAMA ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total de Tarefas", len(df_final))
m2.metric("Tarefas Críticas", len(df_final[df_final['Criticidade'] == 'Crítica']))
m3.metric("Data de Término", df_final['Data Fim'].max().strftime('%d/%m/%Y') if not df_final.empty else "-")
m4.metric("Status Global", "Atenção" if prob_sucesso < 80 else "Pronto")

st.markdown("---")
st.caption("🚀 **Sugestão de Próximo Passo:** Gostaria que eu conectasse este script a uma API de IA real (como a do Gemini ou GPT) para analisar o sentimento dos seus e-mails de projeto automaticamente?")

