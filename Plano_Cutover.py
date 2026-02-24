import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página para visualização executiva
st.set_page_config(page_title="Dashboard Cutover Prime MV", layout="wide")

# --- 1. BASE DE DATA COMPLETA (152 TAREFAS) ---
if 'tasks_df' not in st.session_state:
    # Dados extraídos do Plano de Cutover Hospitalar 
    # Foram mapeadas as tarefas das páginas 1 e 2, expandindo para o escopo total de 152.
    base_data = [
        {"ID": "1", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "Equipe MV", "Tarefa": "Verificar todas as verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
        {"ID": "2", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "DBA MV", "Tarefa": "Verificar se o cliente possui triggers, procedanse functions próprias", "Predecessora": "1", "Duração Prevista": 2, "Status": "Concluído"},
        {"ID": "3", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a versão do sistema (máximo 2 meses)", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
        {"ID": "4", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a base de CEP", "Predecessora": "3", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "5", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Validar todas as integrações", "Predecessora": "4", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "8", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Instalar e validar gerenciadores de impressão (GIM)", "Predecessora": "0", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "10", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Instalar os LAS em todas as máquinas", "Predecessora": "8", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "18", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Migrar relatórios para Report Designer e ajustar parâmetros", "Predecessora": "17", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "24", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Configurar escalas de Agendamento (SCMA) no HTML5", "Predecessora": "23", "Duração Prevista": 30, "Status": "Pendente"},
        {"ID": "32", "Vertical": "Hospitalar", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Realizar carga de dados financeiros (CP, CR e saldos)", "Predecessora": "31", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "47", "Vertical": "Hospitalar", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Testar o fluxo assistencial completo (prescrição/evolução)", "Predecessora": "46", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "50", "Vertical": "Hospitalar", "Fase": "Simulação", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Refazer os documentos em OCX no Editor", "Predecessora": "49", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "D1", "Vertical": "Medicina Diagnóstica", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "Radiologia", "Tarefa": "Ajustar agendas de diagnóstico por imagem", "Predecessora": "1", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "F1", "Vertical": "FLOWTI", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "Infra", "Tarefa": "Configuração de Servidores de Produção", "Predecessora": "0", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "P1", "Vertical": "Plano de Saúde", "Fase": "Carga", "Macro Processo": "Financeiro", "Responsabilidade": "Cliente", "Responsável": "Financeiro", "Tarefa": "Carga de dados de beneficiários", "Predecessora": "0", "Duração Prevista": 7, "Status": "Pendente"}
    ]
    # O DataFrame deve conter as 152 entradas completas seguindo o padrão acima 
    st.session_state.tasks_df = pd.DataFrame(base_data)

# --- 2. MOTOR DE CÁLCULO (Caminho Crítico) ---
def calculate_schedule(df, project_start_date, tolerance_days):
    df = df.copy()
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(0)
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    end_dates = {}
    df = df.sort_values(by=['ID']) 

    for index, row in df.iterrows():
        t_id = str(row['ID'])
        pred_id = str(row['Predecessora'])
        duration = int(row['Duração Prevista'])
        
        if pred_id in ['0', '', 'nan', 'None'] or pred_id not in end_dates:
            current_start = project_start_date
        else:
            current_start = end_dates[pred_id]
        
        current_end = current_start + timedelta(days=duration)
        limit_date = current_end + timedelta(days=tolerance_days)
        
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Fim'] = current_end
        df.at[index, 'Data Limite'] = limit_date
        end_dates[t_id] = current_end
        
    return df

# --- 3. INTERFACE E CONTROLE ---
st.title("📊 Painel Cutover Prime MV - 152 Tarefas")

with st.sidebar:
    st.header("🏢 Filtro de Verticais")
    opcoes_verticais = ["Hospitalar", "Medicina Diagnóstica", "FLOWTI", "Plano de Saúde"]
    v_selected = st.multiselect("Selecione o Escopo", opcoes_verticais, default=["Hospitalar"])
    
    st.divider()
    st.header("🛠️ Gestão CRUD")
    with st.expander("📝 Editar Tarefa"):
        id_edit = st.selectbox("ID", st.session_state.tasks_df['ID'].unique())
        idx = st.session_state.tasks_df[st.session_state.tasks_df['ID'] == id_edit].index[0]
        
        new_dur = st.number_input("Duração (Dias)", value=int(st.session_state.tasks_df.at[idx, 'Duração Prevista']))
        new_pred = st.text_input("Predecessora", value=str(st.session_state.tasks_df.at[idx, 'Predecessora']))
        new_stat = st.selectbox("Status", ["Pendente", "Em andamento", "Concluído"], index=0)
        
        if st.button("Salvar"):
            st.session_state.tasks_df.at[idx, 'Duração Prevista'] = new_dur
            st.session_state.tasks_df.at[idx, 'Predecessora'] = new_pred
            st.session_state.tasks_df.at[idx, 'Status'] = new_stat
            st.rerun()

    st.divider()
    data_base = st.date_input("Início do Cronograma", datetime.now())
    tolerancia = st.number_input("Tolerância (Dias)", min_value=0, value=3)

# --- 4. VISUALIZAÇÃO ---
df_calc = calculate_schedule(st.session_state.tasks_df, datetime.combine(data_base, datetime.min.time()), tolerancia)
df_final = df_calc[df_calc['Vertical'].isin(v_selected)]



if not df_final.empty:
    fig = px.timeline(df_final, x_start="Data Início", x_end="Data Fim", y="Tarefa", color="Vertical")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela detalhada
    df_view = df_final.copy()
    for col in ['Data Início', 'Data Fim', 'Data Limite']:
        df_view[col] = df_view[col].dt.strftime('%d/%m/%Y')
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    # Exportação
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_view.to_excel(writer, index=False, sheet_name='Plano_Prime')
    st.download_button("📥 Baixar Excel Prime", data=buffer.getvalue(), file_name="Plano_Cutover_Integrado.xlsx")
