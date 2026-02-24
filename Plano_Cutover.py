import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página para visualização executiva
st.set_page_config(page_title="Dashboard Cutover Prime MV", layout="wide")

# --- 1. DEFINIÇÃO DA BASE DE DADOS (DADOS DAS FONTES) ---
if 'tasks_df' not in st.session_state:
    # Aqui devem ser inseridas as 152 tarefas extraídas do PDF
    base_data = [
        {"ID": "1", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "Equipe MV", "Tarefa": "Verificar todas as verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
        {"ID": "2", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "DBA MV", "Tarefa": "Verificar se o cliente possui triggers, procedanse functions próprias", "Predecessora": "1", "Duração Prevista": 2, "Status": "Concluído"},
        {"ID": "3", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a versão do sistema", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
        # ... Adicione as outras 149 tarefas aqui seguindo este padrão
        {"ID": "D1", "Vertical": "Medicina Diagnóstica", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "Radiologia", "Tarefa": "Ajustar agendas de diagnóstico por imagem", "Predecessora": "1", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "F1", "Vertical": "FLOWTI", "Fase": "Infra", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "Infra", "Tarefa": "Configuração de Servidores", "Predecessora": "0", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "P1", "Vertical": "Plano de Saúde", "Fase": "Carga", "Macro Processo": "Financeiro", "Responsabilidade": "Cliente", "Responsável": "Financeiro", "Tarefa": "Carga de dados de beneficiários", "Predecessora": "0", "Duração Prevista": 7, "Status": "Pendente"},
    ]
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

# --- 3. INTERFACE E FILTROS (Correção do NameError) ---
st.title("📊 Painel Cutover Prime MV - Gestão Integrada")

with st.sidebar:
    st.header("🏢 Configuração do Escopo")
    
    # DEFINIÇÃO DA VARIÁVEL ANTES DO USO (Evita o NameError)
    opcoes_verticais = ["Hospitalar", "Medicina Diagnóstica", "FLOWTI", "Plano de Saúde"]
    
    v_selected = st.multiselect(
        "Selecione as Verticais do Programa", 
        options=opcoes_verticais, 
        default=["Hospitalar"]
    )
    
    st.divider()
    st.header("🛠️ Edição e CRUD")
    
    # Seção para Editar tarefas existentes
    with st.expander("📝 Editar Tarefa Selecionada"):
        id_edit = st.selectbox("ID da Tarefa", st.session_state.tasks_df['ID'].unique())
        idx = st.session_state.tasks_df[st.session_state.tasks_df['ID'] == id_edit].index[0]
        
        new_dur = st.number_input("Duração (Dias)", value=int(st.session_state.tasks_df.at[idx, 'Duração Prevista']))
        new_pred = st.text_input("Predecessora", value=str(st.session_state.tasks_df.at[idx, 'Predecessora']))
        new_status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluído"], 
                                   index=["Pendente", "Em andamento", "Concluído"].index(st.session_state.tasks_df.at[idx, 'Status']))
        
        if st.button("Salvar Alterações"):
            st.session_state.tasks_df.at[idx, 'Duração Prevista'] = new_dur
            st.session_state.tasks_df.at[idx, 'Predecessora'] = new_pred
            st.session_state.tasks_df.at[idx, 'Status'] = new_status
            st.rerun()

    st.divider()
    data_base = st.date_input("Início do Cutover", datetime.now())
    tolerancia = st.number_input("Tolerância (Dias)", min_value=0, value=3)

# --- 4. PROCESSAMENTO E VISUALIZAÇÃO ---
df_calc = calculate_schedule(st.session_state.tasks_df, datetime.combine(data_base, datetime.min.time()), tolerancia)
df_final = df_calc[df_calc['Vertical'].isin(v_selected)]



if not df_final.empty:
    st.subheader(f"🖼️ Cronograma Integrado - {len(df_final)} Tarefas")
    
    fig = px.timeline(
        df_final, 
        x_start="Data Início", 
        x_end="Data Fim", 
        y="Tarefa", 
        color="Vertical",
        hover_data=["ID", "Predecessora", "Status"],
        color_discrete_map={
            "Hospitalar": "#004a88", 
            "Medicina Diagnóstica": "#00a1ab", 
            "FLOWTI": "#f39200", 
            "Plano de Saúde": "#e30613"
        }
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

    # Exportação para Excel
    df_view = df_final.copy()
    for col in ['Data Início', 'Data Fim', 'Data Limite']:
        df_view[col] = df_view[col].dt.strftime('%d/%m/%Y')
    
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_view.to_excel(writer, index=False, sheet_name='Plano_Cutover')
    
    st.download_button("📥 Baixar Plano Integrado (Excel)", data=buffer.getvalue(), file_name="Plano_Cutover_Integrado.xlsx")
else:
    st.warning("Selecione ao menos uma vertical na barra lateral.")
