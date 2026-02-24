import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(page_title="Painel Cutover Hospitalar MV", layout="wide")

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
# Mantém os dados na memória durante a navegação
if 'tasks_df' not in st.session_state:
    initial_data = [
        {"ID": "1", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "Consultoria", "Tarefa": "Verificar verticais envolvidas", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
        {"ID": "2", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Verificar triggers/procedures próprias", "Predecessora": "1", "Duração Prevista": 2, "Status": "Concluído"},
        {"ID": "3", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Atualizar versão do sistema", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
        {"ID": "18", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Migrar relatórios Report Designer", "Predecessora": "3", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "50", "Fase": "Simulação", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Refazer documentos OCX no Editor", "Predecessora": "18", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "60", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Acompanhar confirmação cirúrgica", "Predecessora": "50", "Duração Prevista": 5, "Status": "Pendente"}
    ] # Adicione aqui as 60 tarefas para a carga inicial completa
    st.session_state.tasks_df = pd.DataFrame(initial_data)

def calculate_schedule(df, project_start_date, tolerance_days):
    df = df.copy()
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(0)
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Predecessora'] = df['Predecessora'].astype(str).str.strip()
    
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    # Ordenação lógica para garantir o cálculo de predecessoras
    df['ID_sort'] = pd.to_numeric(df['ID'], errors='coerce')
    df = df.sort_values('ID_sort').drop(columns=['ID_sort'])
    
    end_dates = {}
    for index, row in df.iterrows():
        task_id = row['ID']
        pred_id = row['Predecessora']
        duration = int(row['Duração Prevista'])
        
        if pred_id in ['0', '', 'None'] or pred_id not in end_dates:
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

# --- SIDEBAR: GERENCIAMENTO (CRUD) ---
with st.sidebar:
    st.header("📋 Gerenciar Tarefas")
    
    with st.expander("🆕 Cadastrar Nova Tarefa"):
        new_id = st.text_input("ID da Tarefa")
        new_fase = st.selectbox("Fase", ["Planejamento", "Pré Go Live", "Carga", "Simulação", "Pós Go Live"])
        new_macro = st.text_input("Macro Processo")
        new_resp_tipo = st.selectbox("Responsabilidade", ["MV", "Cliente", "Outros"])
        new_resp_nome = st.text_input("Nome do Responsável")
        new_tarefa = st.text_area("Descrição da Tarefa")
        new_pred = st.text_input("ID Predecessora", value="0")
        new_dur = st.number_input("Duração (Dias)", min_value=0, value=1)
        new_status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluído"])
        
        if st.button("Adicionar Item"):
            new_row = {
                "ID": new_id, "Fase": new_fase, "Macro Processo": new_macro, 
                "Responsabilidade": new_resp_tipo, "Responsável": new_resp_nome, 
                "Tarefa": new_tarefa, "Predecessora": new_pred, 
                "Duração Prevista": new_dur, "Status": new_status
            }
            st.session_state.tasks_df = pd.concat([st.session_state.tasks_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Tarefa adicionada!")

    with st.expander("✏️ Editar/Excluir Tarefa"):
        target_id = st.selectbox("Selecione o ID", st.session_state.tasks_df['ID'].unique())
        idx = st.session_state.tasks_df[st.session_state.tasks_df['ID'] == target_id].index[0]
        
        edit_status = st.selectbox("Atualizar Status", ["Pendente", "Em andamento", "Concluído"], 
                                   index=["Pendente", "Em andamento", "Concluído"].index(st.session_state.tasks_df.at[idx, 'Status']))
        edit_dur = st.number_input("Atualizar Duração", value=int(st.session_state.tasks_df.at[idx, 'Duração Prevista']))
        
        col_ed1, col_ed2 = st.columns(2)
        if col_ed1.button("Salvar Alterações"):
            st.session_state.tasks_df.at[idx, 'Status'] = edit_status
            st.session_state.tasks_df.at[idx, 'Duração Prevista'] = edit_dur
            st.rerun()
            
        if col_ed2.button("Excluir Tarefa"):
            st.session_state.tasks_df = st.session_state.tasks_df.drop(idx).reset_index(drop=True)
            st.rerun()

    st.divider()
    st.header("⚙️ Configurações de Projeto")
    proj_nome = st.text_input("Nome do Projeto", "Migração MV Hospitalar")
    data_base = st.date_input("Início do Cronograma", datetime.now(), format="DD/MM/YYYY")
    tolerancia = st.number_input("Tolerância (Dias)", min_value=0, value=3)

# --- PROCESSAMENTO E DASHBOARD ---
df_calculado = calculate_schedule(st.session_state.tasks_df, datetime.combine(data_base, datetime.min.time()), tolerancia)

st.title(f"🚀 Dashboard Cutover: {proj_nome}")

# Filtros Rápidos
f_resp = st.multiselect("Filtrar por Responsabilidade", df_calculado['Responsabilidade'].unique(), default=df_calculado['Responsabilidade'].unique())
df_filtered = df_calculado[df_calculado['Responsabilidade'].isin(f_resp)]

# Gráfico de Gantt
if not df_filtered.empty:
    fig = px.timeline(df_filtered, x_start="Data Início", x_end="Data Fim", y="Tarefa", color="Status",
                      hover_data=["ID", "Responsável", "Data Limite"],
                      color_discrete_map={"Concluído": "#2E7D32", "Em andamento": "#F9A825", "Pendente": "#C62828"})
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela formatada
    df_disp = df_filtered.copy()
    for col in ['Data Início', 'Data Fim', 'Data Limite']:
        df_disp[col] = df_disp[col].dt.strftime('%d/%m/%Y')
    
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    # Exportar Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_disp.to_excel(writer, index=False, sheet_name='Plano_Cutover')
    st.download_button(label="📥 Baixar Plano em Excel", data=buffer.getvalue(), 
                       file_name=f"Cutover_{proj_nome}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
