import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(page_title="Painel Cutover Hospitalar MV", layout="wide")

def calculate_schedule(df, project_start_date, tolerance_days):
    df = df.copy()
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(0)
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Predecessora'] = df['Predecessora'].astype(str).str.strip()
    
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    end_dates = {}
    # Ordenar por ID para garantir que as predecessoras sejam calculadas antes das dependentes
    df['ID_Int'] = pd.to_numeric(df['ID'], errors='coerce')
    df = df.sort_values('ID_Int').drop(columns=['ID_Int'])

    for index, row in df.iterrows():
        task_id = row['ID']
        pred_id = row['Predecessora']
        duration = int(row['Duração Prevista'])
        
        # Lógica de início: se for a primeira tarefa ou a predecessora não existir/for 0
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

# Base de Dados completa conforme Plano de Cutover Hospitalar 
tasks_data = [
    {"ID": "1", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Consultoria", "Tarefa": "Verificar todas as verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
    {"ID": "2", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Verificar se o cliente possui triggers, procedures e functions próprias", "Predecessora": "1", "Duração Prevista": 2, "Status": "Concluído"},
    {"ID": "3", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Atualizar a versão do sistema", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
    {"ID": "4", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Atualizar a base de CEP", "Predecessora": "3", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "5", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar todas as integrações", "Predecessora": "4", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "6", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar funcionalidades e configurações multiempresa", "Predecessora": "5", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "7", "Fase": "Pré Go Live", "Macro Processo": "Faturamento", "Responsabilidade": "Cliente", "Responsável": "Faturamento", "Tarefa": "Validar processo automático de autorização hospitalar e convênios", "Predecessora": "6", "Duração Prevista": 6, "Status": "Pendente"},
    {"ID": "8", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar e validar os gerenciadores de impressão (GIM)", "Predecessora": "7", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "9", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar máquinas na rede", "Predecessora": "8", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "10", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar os LAS em todas as máquinas", "Predecessora": "9", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "11", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Instalar o Cent Browser em todas as máquinas", "Predecessora": "10", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "12", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Preparar ferramenta de acesso remoto às máquinas dos setores", "Predecessora": "11", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "13", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Revisar tickets impeditivos e não impeditivos", "Predecessora": "12", "Duração Prevista": 0, "Status": "Pendente"},
    {"ID": "14", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Divulgar a lista de login dos usuários para os setores", "Predecessora": "13", "Duração Prevista": 1, "Status": "Pendente"},
    {"ID": "15", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar todos os vínculos/usuários vinculados", "Predecessora": "14", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "16", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Verificar a relação Usuários Prestador (Versão HTML5)", "Predecessora": "15", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "17", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar impressões de fichas de atendimento e guias SADT", "Predecessora": "16", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "18", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Migrar relatórios para o Report Designer e ajustar parâmetros", "Predecessora": "17", "Duração Prevista": 45, "Status": "Pendente"},
    {"ID": "19", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar impressão dos documentos de prontuário", "Predecessora": "18", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "20", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar etiquetas de todos os setores", "Predecessora": "19", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "21", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Testar leitores de códigos de barras de todos os setores", "Predecessora": "20", "Duração Prevista": 6, "Status": "Pendente"},
    {"ID": "22", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Vincular usuários por unidade de internação (HTML5)", "Predecessora": "21", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "23", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Vincular Usuário x Prestador para PEP", "Predecessora": "22", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "24", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Ajustar escalas de Agendamento (SCMA) no HTML5", "Predecessora": "23", "Duração Prevista": 30, "Status": "Pendente"},
    {"ID": "25", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar levantamento de internações no sistema atual", "Predecessora": "24", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "26", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar levantamento de agendamentos cirúrgicos no sistema atual", "Predecessora": "25", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "27", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar agendamentos ambulatoriais", "Predecessora": "26", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "28", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar agendamentos cirúrgicos", "Predecessora": "27", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "29", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "SADT", "Tarefa": "Realizar agendamentos de exames", "Predecessora": "28", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "30", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "SADT", "Tarefa": "Ajustar agendas de diagnóstico por imagem", "Predecessora": "29", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "31", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Realizar internação dos pacientes", "Predecessora": "30", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "32", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Realizar carga de dados financeiros (CP, CR e saldos)", "Predecessora": "31", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "33", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Realizar carga de dados contábeis (saldos)", "Predecessora": "32", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "34", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Alterar o processo do Custo Médio Diário para Custo Médio Mensal", "Predecessora": "33", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "35", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Definir Cartão de Crédito e Débito na tela de Administradora", "Predecessora": "34", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "36", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Ajustar processos de Caixa/Tesouraria (unificados)", "Predecessora": "35", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "37", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Orientar que produtos excedentes nos andares sejam devolvidos", "Predecessora": "36", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "38", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Etiquetar todos os produtos com etiquetas emitidas pelo MV", "Predecessora": "37", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "39", "Fase": "Carga", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Realizar Inventário", "Predecessora": "38", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "40", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Divulgar agenda de alocação dos multiplicadores por setor", "Predecessora": "39", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "41", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Divulgar agenda de alocação do time de migração", "Predecessora": "40", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "42", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Outros", "Responsável": "TI", "Tarefa": "Divulgar agenda de alocação da consultoria por setores", "Predecessora": "41", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "43", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Validar os logins e perfis de acesso na simulação", "Predecessora": "42", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "44", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Criar paciente fictício para validação do ambiente de Produção", "Predecessora": "43", "Duração Prevista": 1, "Status": "Pendente"},
    {"ID": "45", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Verificar o número de estações contratadas e comparar com a real", "Predecessora": "44", "Duração Prevista": 0, "Status": "Pendente"},
    {"ID": "46", "Fase": "Simulação", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Atendimento", "Tarefa": "Testar abertura de atendimentos", "Predecessora": "45", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "47", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Testar o fluxo assistencial (atendimento, evolução, prescrição)", "Predecessora": "46", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "48", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Verificar telas descontinuadas da PEP e ajustar", "Predecessora": "47", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "49", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Executar scripts de ajuste de frequências (SELECT insert into)", "Predecessora": "48", "Duração Prevista": 1, "Status": "Pendente"},
    {"ID": "50", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Refazer os documentos em OCX no Editor", "Predecessora": "49", "Duração Prevista": 45, "Status": "Pendente"},
    {"ID": "51", "Fase": "Simulação", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "SADT", "Tarefa": "Testar solicitação de exames e conferência", "Predecessora": "50", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "52", "Fase": "Simulação", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Testar solicitações diversas para o estoque", "Predecessora": "51", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "53", "Fase": "Simulação", "Macro Processo": "Faturamento", "Responsabilidade": "Cliente", "Responsável": "Faturamento", "Tarefa": "Testar fechamento de contas de faturamento", "Predecessora": "52", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "54", "Fase": "Simulação", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Controladoria", "Tarefa": "Testar recebimento, estorno e cancelamento no caixa", "Predecessora": "53", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "55", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI", "Tarefa": "Fazer backup do banco e guardar configurações testadas", "Predecessora": "54", "Duração Prevista": 1, "Status": "Pendente"},
    {"ID": "56", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "TI", "Tarefa": "Abrir Centex para ST avaliar ambiente", "Predecessora": "55", "Duração Prevista": 0, "Status": "Pendente"},
    {"ID": "57", "Fase": "Pós Go Live", "Macro Processo": "Faturamento", "Responsabilidade": "MV", "Responsável": "Faturamento", "Tarefa": "Monitorar com o setor o relatório de consumo", "Predecessora": "56", "Duração Prevista": 1, "Status": "Pendente"},
    {"ID": "58", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Suprimentos", "Tarefa": "Acompanhar volume de devolução via MV", "Predecessora": "57", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "59", "Fase": "Pós Go Live", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Monitorar prescrições manuais e reportar à direção", "Predecessora": "58", "Duração Prevista": 7, "Status": "Pendente"},
    {"ID": "60", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Assistencial", "Tarefa": "Acompanhar confirmação cirúrgica", "Predecessora": "59", "Duração Prevista": 5, "Status": "Pendente"}
]

# --- SIDEBAR: CONFIGURAÇÕES E FILTROS ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    proj_nome = st.text_input("Nome do Projeto", "Migração MV Hospitalar")
    gp_nome = st.text_input("Gerente de Projetos", "Seu Nome")
    data_base = st.date_input("Início do Cronograma", datetime.now(), format="DD/MM/YYYY")
    tolerancia = st.number_input("Tolerância de Desvio (Dias)", min_value=0, value=3)
    
    st.divider()
    st.header("🔍 Filtros de Exibição")
    df_raw = pd.DataFrame(tasks_data)
    f_resp = st.multiselect("Responsabilidade", df_raw['Responsabilidade'].unique(), default=df_raw['Responsabilidade'].unique())
    f_macro = st.multiselect("Macro Processo", df_raw['Macro Processo'].unique(), default=df_raw['Macro Processo'].unique())
    f_status = st.multiselect("Status da Tarefa", df_raw['Status'].unique(), default=df_raw['Status'].unique())

# --- PROCESSAMENTO ---
dt_start = datetime.combine(data_base, datetime.min.time())
df_full = calculate_schedule(df_raw, dt_start, tolerancia)

# Aplicação dos Filtros
df_filtered = df_full[
    (df_full['Responsabilidade'].isin(f_resp)) & 
    (df_full['Macro Processo'].isin(f_macro)) &
    (df_full['Status'].isin(f_status))
]

# --- DASHBOARD VISUAL ---
st.title(f"🚀 Dashboard Cutover: {proj_nome}")

if not df_filtered.empty:
    # Gráfico de Gantt por Status
    fig = px.timeline(
        df_filtered, 
        x_start="Data Início", 
        x_end="Data Fim", 
        y="Tarefa", 
        color="Status",
        hover_data=["ID", "Responsável", "Data Limite"],
        color_discrete_map={"Concluído": "#2E7D32", "Em andamento": "#F9A825", "Pendente": "#C62828"}
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    fig.update_layout(height=800, xaxis_title="Linha do Tempo (Padrão dd/mm/aaaa)")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Dados
    st.subheader("📑 Detalhamento do Plano de Ação")
    df_disp = df_filtered.copy()
    for col in ['Data Início', 'Data Fim', 'Data Limite']:
        df_disp[col] = df_disp[col].dt.strftime('%d/%m/%Y')
    
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    # Botão de Exportação Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_disp.to_excel(writer, index=False, sheet_name='Plano_Cutover')
    
    st.download_button(
        label="📥 Exportar Cronograma Filtrado (Excel)",
        data=buffer.getvalue(),
        file_name=f"Cutover_{proj_nome}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Nenhum dado encontrado para os filtros aplicados.")

st.caption(f"GP Responsável: {gp_nome} | Tolerância aplicada: {tolerancia} dias.")

