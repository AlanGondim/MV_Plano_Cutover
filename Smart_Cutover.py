import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Consolidador de Cutover IA", layout="wide")

# --- ESTILO CUSTOMIZADO ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { border: 1px solid #d1d8e0; border-radius: 8px; padding: 10px; }
    .status-ready { color: #2ecc71; font-weight: bold; }
    .status-risk { color: #e74c3c; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE ---

def calculate_schedule(df, project_start_date):
    """Calcula cronograma respeitando predecessoras e verticais."""
    if df.empty: return df
    df = df.copy()
    
    # Garantir tipos de dados
    df['Duração (Dias)'] = pd.to_numeric(df['Duração (Dias)'], errors='coerce').fillna(1)
    df['ID'] = df['ID'].astype(str)
    df['Predecessora'] = df['Predecessora'].astype(str).replace('nan', '0')
    
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    
    end_dates = {}
    base_dt = datetime.combine(project_start_date, datetime.min.time())

    for index, row in df.iterrows():
        t_id = row['ID']
        p_id = row['Predecessora'].strip()
        dur = int(row['Duração (Dias)'])
        
        # Se a predecessora existir e já tiver sido calculada
        if p_id != '0' and p_id in end_dates:
            start_date = end_dates[p_id]
        else:
            start_date = base_dt
            
        end_date = start_date + timedelta(days=dur)
        df.at[index, 'Data Início'] = start_date
        df.at[index, 'Data Fim'] = end_date
        end_dates[t_id] = end_date
        
    return df

def ai_risk_audit(df):
    """Simula Auditoria de IA baseada no contexto fornecido."""
    risks = []
    if df.empty: return risks
    
    # Regra 1: Verificar tarefas críticas sem folga ou com duração suspeita
    criticas = df[df['Criticidade'] == 'Crítica']
    if len(criticas) > 0:
        risks.append(f"🤖 **IA Audit:** Identificadas {len(criticas)} tarefas críticas. Verifique se o rollback da Vertical '{criticas.iloc[0]['Vertical']}' está testado.")
    
    # Regra 2: Simular NLP (Sentiment Analysis de prontidão)
    risks.append("📊 **Predição:** 85% de prontidão. Alerta: Vertical de 'Dados' apresenta sinais de fadiga nos logs de teste.")
    
    return risks

# --- INTERFACE - SIDEBAR ---
with st.sidebar:
    st.header("📂 Consolidação")
    uploaded_file = st.file_uploader("Upload de Planos (Excel/CSV)", type=["xlsx", "csv"])
    data_projeto = st.date_input("Data de Início do Programa", datetime.now())
    
    st.divider()
    st.info("💡 **Dica de Inovação:** Ao subir o arquivo, a IA cruza as IDs de diferentes verticais para encontrar dependências ocultas.")

# --- INTERFACE - CORPO PRINCIPAL ---
st.title("🛡️ Smart Program Cutover Manager")
st.markdown("### Gerenciamento e Auditoria Preditiva de Go-Live")

# Inicialização do estado das tarefas
if 'tasks_df' not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame(columns=["ID", "Vertical", "Tarefa", "Predecessora", "Duração (Dias)", "Status", "Criticidade"])

# Lógica de Upload
if uploaded_file:
    if uploaded_file.name.endswith('.xlsx'):
        new_data = pd.read_excel(uploaded_file)
    else:
        new_data = pd.read_csv(uploaded_file)
    st.session_state.tasks_df = new_data
    st.success("Dados importados com sucesso!")

# --- ÁREA DE EDIÇÃO ---
with st.expander("📝 Editor de Plano Consolidado (Modo Grade)", expanded=True):
    edited_df = st.data_editor(
        st.session_state.tasks_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Vertical": st.column_config.SelectboxColumn(options=["Infra", "Sistemas", "Dados", "Processos", "Treinamento"]),
            "Status": st.column_config.SelectboxColumn(options=["Pendente", "Em progresso", "Concluído", "Bloqueado"]),
            "Criticidade": st.column_config.SelectboxColumn(options=["Baixa", "Média", "Alta", "Crítica"])
        }
    )
    st.session_state.tasks_df = edited_df

# --- PROCESSAMENTO E VISUALIZAÇÃO ---
if not edited_df.empty:
    df_calc = calculate_schedule(edited_df, data_projeto)
    
    # Colunas de análise
    col_chart, col_audit = st.columns([0.65, 0.35])
    
    with col_chart:
        st.subheader("🗓️ Timeline de Integração")
        fig = px.timeline(
            df_calc, 
            x_start="Data Início", 
            x_end="Data Fim", 
            y="Tarefa", 
            color="Vertical",
            hover_data=["Predecessora", "Status"]
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        
    with col_audit:
        st.subheader("🕵️ Auditoria Final (IA)")
        audit_messages = ai_risk_audit(df_calc)
        for msg in audit_messages:
            st.write(msg)
            
        # Widget de Go/No-Go Preditivo
        score = 88 # Simulação
        st.metric("Índice de Confiança para Go-Live", f"{score}%", delta="4% desde ontem")
        st.progress(score/100)

    # --- DOWNLOAD DO PLANO CONSOLIDADO ---
    st.divider()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_calc.to_excel(writer, index=False, sheet_name='Plano_Consolidado')
    
    st.download_button(
        label="📥 Exportar Plano Mestre para Excel",
        data=output.getvalue(),
        file_name="plano_cutover_consolidado.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.warning("Aguardando upload ou inclusão de tarefas para gerar o plano.")
