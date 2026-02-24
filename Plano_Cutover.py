import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(page_title="Painel Cutover Hospitalar", layout="wide")

def calculate_schedule(df, project_start_date, tolerance_days):
    df = df.copy()
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(0)
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Predecessora'] = df['Predecessora'].astype(str).str.strip()
    
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    end_dates = {}
    for index, row in df.iterrows():
        task_id = row['ID']
        pred_id = row['Predecessora']
        duration = int(row['Duração Prevista'])
        
        if pred_id in ['0', '', task_id] or pred_id not in end_dates:
            current_start = project_start_date
        else:
            current_start = end_dates[pred_id]
        
        current_end = current_start + timedelta(days=duration)
        limit_date = current_end + timedelta(days=tolerance_days)
        
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Fim'] = current_end
        df.at[index, 'Data Limite'] = limit_date
        end_dates[task_id] = current_end
    return df

# Base de Dados Completa baseada nos documentos 
tasks_data = [
    {"ID": "1", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Equipe MV", "Tarefa": "Verificar todas as verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
    {"ID": "2", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "DBA MV", "Tarefa": "Verificar triggers e procedures próprias", "Predecessora": "1", "Duração Prevista": 1, "Status": "Concluído"},
    {"ID": "3", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a versão do sistema", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
    {"ID": "4", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a base de CEP", "Predecessora": "3", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "5", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Validar todas as integrações", "Predecessora": "4", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "8", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Instalar e validar GIM (Impressão)", "Predecessora": "5", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "18", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Migrar relatórios Report Designer", "Predecessora": "8", "Duração Prevista": 45, "Status": "Pendente"},
    {"ID": "24", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Gestor Recepção", "Tarefa": "Configurar escalas HTML5", "Predecessora": "18", "Duração Prevista": 30, "Status": "Pendente"},
    {"ID": "27", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Ambulatório", "Tarefa": "Realizar agendamentos ambulatoriais", "Predecessora": "24", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "32", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Financeiro", "Tarefa": "Carga CP/CR/Saldos", "Predecessora": "27", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "47", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Líder Enfermagem", "Tarefa": "Testar fluxo assistencial", "Predecessora": "32", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "50", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Refazer documentos OCX", "Predecessora": "47", "Duração Prevista": 45, "Status": "Pendente"},
    {"ID": "60", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "C. Cirúrgico", "Tarefa": "Confirmar cirurgias", "Predecessora": "50", "Duração Prevista": 2, "Status": "Pendente"}
]

# --- INTERFACE ---
st.title("📊 Gestão de Cutover MV Hospitalar")

with st.sidebar:
    st.header("⚙️ Configurações")
    projeto = st.text_input("Projeto", "Migração MV")
    gp = st.text_input("Gerente", "Nome do GP")
    data_inicio = st.date_input("Data de Início", datetime.now(), format="DD/MM/YYYY")
    tolerancia = st.number_input("Tolerância (Dias)", min_value=0, value=3)
    
    st.divider()
    st.header("🔍 Filtros Gerenciais")
    df_raw = pd.DataFrame(tasks_data)
    f_resp = st.multiselect("Responsabilidade", df_raw['Responsabilidade'].unique(), default=df_raw['Responsabilidade'].unique())
    f_macro = st.multiselect("Macro Processo", df_raw['Macro Processo'].unique(), default=df_raw['Macro Processo'].unique())
    f_status = st.multiselect("Status da Tarefa", df_raw['Status'].unique(), default=df_raw['Status'].unique())

# --- CÁLCULOS ---
dt_start = datetime.combine(data_inicio, datetime.min.time())
df_full = calculate_schedule(df_raw, dt_start, tolerancia)

# Filtro dinâmico
df_filtered = df_full[
    (df_full['Responsabilidade'].isin(f_resp)) & 
    (df_full['Macro Processo'].isin(f_macro)) &
    (df_full['Status'].isin(f_status))
]

# --- DASHBOARD ---
if not df_filtered.empty:
    st.subheader(f"📅 Cronograma de Execução: {projeto}")
    fig = px.timeline(df_filtered, x_start="Data Início", x_end="Data Fim", y="Tarefa", color="Status", 
                      hover_data=["Responsável", "Data Limite"], title="Gantt por Status")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela formatada para exibição
    df_disp = df_filtered.copy()
    for col in ['Data Início', 'Data Fim', 'Data Limite']:
        df_disp[col] = df_disp[col].dt.strftime('%d/%m/%Y')
    
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    # --- BOTÃO EXCEL ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_disp.to_excel(writer, index=False, sheet_name='Cutover')
    
    st.download_button(
        label="📥 Baixar Plano em Excel",
        data=buffer.getvalue(),
        file_name=f"Cutover_{projeto}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Nenhuma tarefa encontrada com os filtros selecionados.")
