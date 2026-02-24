import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(page_title="Painel Cutover Hospitalar MV", layout="wide")

# --- BASE DE DADOS OFICIAL (60 TAREFAS) ---
if 'tasks_df' not in st.session_state:
    raw_data = [
        {"ID": "1", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "Consultoria", "Tarefa": "Verificar todas as verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
        {"ID": "2", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Verificar triggers, procedures e functions próprias", "Predecessora": "1", "Duração Prevista": 2, "Status": "Concluído"},
        {"ID": "3", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Atualizar a versão do sistema", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
        {"ID": "4", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Atualizar a base de CEP", "Predecessora": "3", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "5", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar todas as integrações", "Predecessora": "4", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "6", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar funcionalidades multiempresa", "Predecessora": "5", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "7", "Fase": "Pré Go Live", "Macro Processo": "Faturamento", "Responsabilidade": "Cliente", "Responsável": "Faturamento", "Tarefa": "Validar autorização hospitalar e convênios", "Predecessora": "6", "Duração Prevista": 6, "Status": "Pendente"},
        {"ID": "8", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar gerenciadores de impressão (GIM)", "Predecessora": "7", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "9", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar máquinas na rede", "Predecessora": "8", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "10", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar LAS em todas as máquinas", "Predecessora": "9", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "11", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar o Cent Browser em todas as máquinas", "Predecessora": "10", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "12", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Preparar ferramenta de acesso remoto", "Predecessora": "11", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "13", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Revisar tickets impeditivos e não impeditivos", "Predecessora": "12", "Duração Prevista": 0, "Status": "Pendente"},
        {"ID": "14", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Divulgar a lista de login para os setores", "Predecessora": "13", "Duração Prevista": 1, "Status": "Pendente"},
        {"ID": "15", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar todos os vínculos e usuários", "Predecessora": "14", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "16", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Verificar relação Usuários Prestador HTML5", "Predecessora": "15", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "17", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar impressões de fichas e guias SADT", "Predecessora": "16", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "18", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Migrar relatórios para Report Designer", "Predecessora": "17", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "19", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar impressão de documentos de prontuário", "Predecessora": "18", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "20", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar etiquetas de todos os setores", "Predecessora": "19", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "21", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar leitores de código de barras", "Predecessora": "20", "Duração Prevista": 6, "Status": "Pendente"},
        {"ID": "22", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Vincular usuários por unidade de internação", "Predecessora": "21", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "23", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Vincular Usuário x Prestador para PEP", "Predecessora": "22", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "24", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Ajustar escalas de Agendamento (SCMA)", "Predecessora": "23", "Duração Prevista": 30, "Status": "Pendente"},
        {"ID": "25", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Levantamento de internações no sistema atual", "Predecessora": "24", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "26", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Levantamento agendamentos cirúrgicos atual", "Predecessora": "25", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "27", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar agendamentos ambulatoriais", "Predecessora": "26", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "28", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar agendamentos cirúrgicos", "Predecessora": "27", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "29", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "SADT", "Tarefa": "Realizar agendamentos de exames", "Predecessora": "28", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "30", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "SADT", "Tarefa": "Ajustar agendas de diagnóstico por imagem", "Predecessora": "29", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "31", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar internação dos pacientes", "Predecessora": "30", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "32", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Carga de dados financeiros (CP, CR, Saldos)", "Predecessora": "31", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "33", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Carga de dados contábeis (saldos)", "Predecessora": "32", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "34", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Ajuste Custo Médio Diário para Mensal", "Predecessora": "33", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "35", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Definir Administradora de Cartões", "Predecessora": "34", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "36", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Ajustar processos de Caixa/Tesouraria", "Predecessora": "35", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "37", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Orientar devolução de produtos excedentes", "Predecessora": "36", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "38", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Etiquetar produtos com etiquetas MV", "Predecessora": "37", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "39", "Fase": "Carga", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Realizar Inventário Geral", "Predecessora": "38", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "40", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Divulgar agenda de alocação multiplicadores", "Predecessora": "39", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "41", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Divulgar agenda time de migração", "Predecessora": "40", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "42", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Outros", "Responsável": "TI", "Tarefa": "Divulgar agenda da consultoria", "Predecessora": "41", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "43", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar logins e perfis na simulação", "Predecessora": "42", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "44", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Criar paciente fictício para Produção", "Predecessora": "43", "Duração Prevista": 1, "Status": "Pendente"},
        {"ID": "45", "Fase": "Planejamento", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Verificar estações contratadas x real", "Predecessora": "44", "Duração Prevista": 0, "Status": "Pendente"},
        {"ID": "46", "Fase": "Simulação", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Testar abertura de atendimentos", "Predecessora": "45", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "47", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Testar fluxo assistencial completo", "Predecessora": "46", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "48", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Ajustar telas descontinuadas PEP", "Predecessora": "47", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "49", "Fase": "Simulação", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Scripts de ajuste de frequências", "Predecessora": "48", "Duração Prevista": 1, "Status": "Pendente"},
        {"ID": "50", "Fase": "Simulação", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Refazer documentos OCX no Editor", "Predecessora": "49", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "51", "Fase": "Simulação", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "SADT", "Tarefa": "Testar solicitação de exames", "Predecessora": "50", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "52", "Fase": "Simulação", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Testar solicitações para estoque", "Predecessora": "51", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "53", "Fase": "Simulação", "Macro Processo": "Faturamento", "Responsabilidade": "Cliente", "Responsável": "Faturamento", "Tarefa": "Testar fechamento de contas", "Predecessora": "52", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "54", "Fase": "Simulação", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Testar recebimento/estorno no caixa", "Predecessora": "53", "Duração Prevista": 5, "Status": "Pendente"},
        {"ID": "55", "Fase": "Simulação", "Macro Processo": "TI", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Backup do banco e configurações finais", "Predecessora": "54", "Duração Prevista": 1, "Status": "Pendente"},
        {"ID": "56", "Fase": "Pré Go Live", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Abrir Centex para avaliação ST", "Predecessora": "55", "Duração Prevista": 0, "Status": "Pendente"},
        {"ID": "57", "Fase": "Pós Go Live", "Macro Processo": "Faturamento", "Responsabilidade": "MV", "Responsável": "Faturamento", "Tarefa": "Monitorar relatório de consumo", "Predecessora": "56", "Duração Prevista": 1, "Status": "Pendente"},
        {"ID": "58", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Acompanhar devoluções via MV", "Predecessora": "57", "Duração Prevista": 2, "Status": "Pendente"},
        {"ID": "59", "Fase": "Pós Go Live", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Monitorar prescrições manuais", "Predecessora": "58", "Duração Prevista": 7, "Status": "Pendente"},
        {"ID": "60", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Acompanhar confirmação cirúrgica", "Predecessora": "59", "Duração Prevista": 5, "Status": "Pendente"}
    ]
    st.session_state.tasks_df = pd.DataFrame(raw_data)

# --- FUNÇÃO DE CÁLCULO ---
def calculate_schedule(df, project_start_date, tolerance_days):
    df = df.copy()
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(0)
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Predecessora'] = df['Predecessora'].astype(str).str.strip()
    
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    # Ordenação técnica para cálculo sequencial
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

# --- SIDEBAR: CRUD E CONFIGURAÇÕES ---
with st.sidebar:
    st.header("📋 Gestão do Plano")
    
    with st.expander("🆕 Nova Tarefa"):
        n_id = st.text_input("ID")
        n_fase = st.selectbox("Fase", ["Planejamento", "Pré Go Live", "Carga", "Simulação", "Pós Go Live"])
        n_macro = st.text_input("Macro Processo")
        n_resp_t = st.selectbox("Responsabilidade", ["Cliente", "MV", "Outros"])
        n_resp_n = st.text_input("Responsável")
        n_tarefa = st.text_area("Descrição")
        n_pred = st.text_input("Predecessora ID", value="0")
        n_dur = st.number_input("Duração", min_value=0, value=1)
        n_stat = st.selectbox("Status", ["Pendente", "Em andamento", "Concluído"])
        if st.button("Adicionar"):
            new_row = {"ID": n_id, "Fase": n_fase, "Macro Processo": n_macro, "Responsabilidade": n_resp_t, 
                       "Responsável": n_resp_n, "Tarefa": n_tarefa, "Predecessora": n_pred, "Duração Prevista": n_dur, "Status": n_stat}
            st.session_state.tasks_df = pd.concat([st.session_state.tasks_df, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

    with st.expander("✏️ Editar / Excluir"):
        sel_id = st.selectbox("Selecione ID", st.session_state.tasks_df['ID'].unique())
        idx = st.session_state.tasks_df[st.session_state.tasks_df['ID'] == sel_id].index[0]
        
        up_stat = st.selectbox("Status Atual", ["Pendente", "Em andamento", "Concluído"], 
                               index=["Pendente", "Em andamento", "Concluído"].index(st.session_state.tasks_df.at[idx, 'Status']))
        up_dur = st.number_input("Duração Atual", value=int(st.session_state.tasks_df.at[idx, 'Duração Prevista']))
        
        c1, c2 = st.columns(2)
        if c1.button("Salvar"):
            st.session_state.tasks_df.at[idx, 'Status'] = up_stat
            st.session_state.tasks_df.at[idx, 'Duração Prevista'] = up_dur
            st.rerun()
        if c2.button("Remover"):
            st.session_state.tasks_df = st.session_state.tasks_df.drop(idx).reset_index(drop=True)
            st.rerun()

    st.divider()
    proj_n = st.text_input("Projeto", "Migração MV Hospitalar")
    data_b = st.date_input("Data Base", datetime.now())
    toler = st.number_input("Tolerância", min_value=0, value=3)

# --- EXECUÇÃO E DASHBOARD ---
df_res = calculate_schedule(st.session_state.tasks_df, datetime.combine(data_b, datetime.min.time()), toler)

st.title(f"🚀 Dashboard: {proj_n}")

# Filtros Rápidos
f_macro = st.multiselect("Filtrar Macro Processo", df_res['Macro Processo'].unique(), default=df_res['Macro Processo'].unique())
df_f = df_res[df_res['Macro Processo'].isin(f_macro)]

if not df_f.empty:
    fig = px.timeline(df_f, x_start="Data Início", x_end="Data Fim", y="Tarefa", color="Status",
                      hover_data=["ID", "Responsável", "Data Limite"],
                      color_discrete_map={"Concluído": "#2E7D32", "Em andamento": "#F9A825", "Pendente": "#C62828"})
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

    # Exibição Final
    df_v = df_f.copy()
    for c in ['Data Início', 'Data Fim', 'Data Limite']: df_v[c] = df_v[c].dt.strftime('%d/%m/%Y')
    st.dataframe(df_v, use_container_width=True, hide_index=True)

    # Exportação
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_v.to_excel(writer, index=False, sheet_name='Plano')
    st.download_button("📥 Baixar Excel", data=buffer.getvalue(), file_name="Plano_Cutover.xlsx")
