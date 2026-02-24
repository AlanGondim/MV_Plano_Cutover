import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuração da página para modo Wide
st.set_page_config(page_title="Gestão de Cutover Hospitalar - MV", layout="wide")

# --- LÓGICA DE CÁLCULO DO CRONOGRAMA ---
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
        
        # Define a data de início baseada na predecessora
        if pred_id in ['0', '', task_id] or pred_id not in end_dates:
            current_start = project_start_date
        else:
            current_start = end_dates[pred_id]
        
        current_end = current_start + timedelta(days=duration)
        # Data Limite = Fim Previsto + Tolerância (Desvio)
        limit_date = current_end + timedelta(days=tolerance_days)
        
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Fim'] = current_end
        df.at[index, 'Data Limite'] = limit_date
        end_dates[task_id] = current_end
        
    return df

# --- BASE DE DADOS COMPLETA (60 TAREFAS) ---
tasks_data = [
    {"ID": "1", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Equipe MV", "Tarefa": "Verificar verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
    {"ID": "2", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "DBA MV", "Tarefa": "Verificar triggers e functions próprias", "Predecessora": "1", "Duração Prevista": 1, "Status": "Concluído"},
    {"ID": "3", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a versão do sistema", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
    {"ID": "4", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a base de CEP", "Predecessora": "3", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "5", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Validar todas as integrações", "Predecessora": "4", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "6", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Validar funcionalidades multiempresa", "Predecessora": "5", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "7", "Fase": "Pré Go Live", "Macro Processo": "Faturamento", "Responsabilidade": "Cliente", "Responsável": "Gestor Faturamento", "Tarefa": "Validar processo de autorização hospitalar", "Predecessora": "6", "Duração Prevista": 6, "Status": "Pendente"},
    {"ID": "8", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Instalar e validar GIM (Impressão)", "Predecessora": "7", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "9", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Instalar máquinas na rede", "Predecessora": "8", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "10", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Instalar LAS em todas as máquinas", "Predecessora": "9", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "11", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Instalar Cent Browser", "Predecessora": "10", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "12", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Ferramenta de acesso remoto", "Predecessora": "11", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "13", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Consultor MV", "Tarefa": "Revisar tickets impeditivos", "Predecessora": "12", "Duração Prevista": 0, "Status": "Pendente"},
    {"ID": "14", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Divulgar lista de logins", "Predecessora": "13", "Duração Prevista": 1, "Status": "Pendente"},
    {"ID": "15", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Validar vínculos de usuários", "Predecessora": "14", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "16", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Verificar relação Usuários Prestador", "Predecessora": "15", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "17", "Fase": "Pré Go Live", "Macro Processo": "Faturamento", "Responsabilidade": "Cliente", "Responsável": "Faturamento", "Tarefa": "Testar impressões de fichas/guias", "Predecessora": "16", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "18", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Migrar relatórios Report Designer", "Predecessora": "17", "Duração Prevista": 45, "Status": "Pendente"},
    {"ID": "19", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Testar impressão de prontuário", "Predecessora": "18", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "20", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "Setores", "Tarefa": "Testar etiquetas de todos os setores", "Predecessora": "19", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "21", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "Setores", "Tarefa": "Testar leitores de código de barras", "Predecessora": "20", "Duração Prevista": 6, "Status": "Pendente"},
    {"ID": "22", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Vincular usuários a unidades", "Predecessora": "21", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "23", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Vincular Usuário x Prestador PEP", "Predecessora": "22", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "24", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Gestor Recepção", "Tarefa": "Configurar escalas HTML5", "Predecessora": "23", "Duração Prevista": 30, "Status": "Pendente"},
    {"ID": "25", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Recepção", "Tarefa": "Levantamento sistema atual", "Predecessora": "24", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "26", "Fase": "Pré Go Live", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Agendamento", "Tarefa": "Levantamento cirurgias atuais", "Predecessora": "25", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "27", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Ambulatório", "Tarefa": "Realizar agendamentos ambulatoriais", "Predecessora": "26", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "28", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Centro Cirúrgico", "Tarefa": "Realizar agendamentos cirúrgicos", "Predecessora": "27", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "29", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "Recepção SADT", "Tarefa": "Realizar agendamentos exames", "Predecessora": "28", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "30", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "Radiologia", "Tarefa": "Migrar diagnóstico por imagem", "Predecessora": "29", "Duração Prevista": 15, "Status": "Pendente"},
    {"ID": "31", "Fase": "Carga", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Internação", "Tarefa": "Realizar internação dos pacientes", "Predecessora": "30", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "32", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Financeiro", "Tarefa": "Carga CP/CR/Saldos", "Predecessora": "31", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "33", "Fase": "Carga", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Contabilidade", "Tarefa": "Carga de dados contábeis", "Predecessora": "32", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "34", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Custo", "Tarefa": "Ajuste Custo Médio Mensal", "Predecessora": "33", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "35", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Financeiro", "Tarefa": "Definir Adm. Cartão", "Predecessora": "34", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "36", "Fase": "Pré Go Live", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Tesouraria", "Tarefa": "Unificar Caixa e Tesouraria", "Predecessora": "35", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "37", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Almoxarifado", "Tarefa": "Devolução produtos excedentes", "Predecessora": "36", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "38", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Estoque Central", "Tarefa": "Etiquetar produtos MV", "Predecessora": "37", "Duração Prevista": 10, "Status": "Pendente"},
    {"ID": "39", "Fase": "Carga", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Almoxarifado", "Tarefa": "Realizar Inventário Geral", "Predecessora": "38", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "40", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "RH/TI", "Tarefa": "Divulgar agenda multiplicadores", "Predecessora": "39", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "41", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Coord. MV", "Tarefa": "Divulgar agenda migração", "Predecessora": "40", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "42", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Coord. MV", "Tarefa": "Divulgar agenda consultoria", "Predecessora": "41", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "43", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Validar logins na simulação", "Predecessora": "42", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "44", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Criar paciente fictício Produção", "Predecessora": "43", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "45", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Gestão Comercial", "Tarefa": "Verificar estações contratadas", "Predecessora": "44", "Duração Prevista": 0, "Status": "Pendente"},
    {"ID": "46", "Fase": "Simulação", "Macro Processo": "Atendimento", "Responsabilidade": "Cliente", "Responsável": "Recepção", "Tarefa": "Testar abertura atendimentos", "Predecessora": "45", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "47", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Líder Enfermagem", "Tarefa": "Testar fluxo assistencial", "Predecessora": "46", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "48", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "TI/Assistencial", "Tarefa": "Ajustar telas descontinuadas PEP", "Predecessora": "47", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "49", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "DBA Local", "Tarefa": "Scripts de prescrição", "Predecessora": "48", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "50", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Refazer documentos OCX", "Predecessora": "49", "Duração Prevista": 45, "Status": "Pendente"},
    {"ID": "51", "Fase": "Simulação", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "SADT/Enf", "Tarefa": "Testar solicitação exames", "Predecessora": "50", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "52", "Fase": "Simulação", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Almoxarifado", "Tarefa": "Testar solicitações estoque", "Predecessora": "51", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "53", "Fase": "Simulação", "Macro Processo": "Faturamento", "Responsabilidade": "Cliente", "Responsável": "Faturamento", "Tarefa": "Testar fechamento contas", "Predecessora": "52", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "54", "Fase": "Simulação", "Macro Processo": "Controladoria", "Responsabilidade": "Cliente", "Responsável": "Tesouraria", "Tarefa": "Testar recebimento caixa", "Predecessora": "53", "Duração Prevista": 5, "Status": "Pendente"},
    {"ID": "55", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Backup configs testadas", "Predecessora": "54", "Duração Prevista": 1, "Status": "Pendente"},
    {"ID": "56", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Suporte MV", "Tarefa": "Abrir Centex avaliação ST", "Predecessora": "55", "Duração Prevista": 0, "Status": "Pendente"},
    {"ID": "57", "Fase": "Pós Go Live", "Macro Processo": "Faturamento", "Responsabilidade": "MV", "Responsável": "Consultor MV", "Tarefa": "Monitorar consumo faturamento", "Predecessora": "56", "Duração Prevista": 0, "Status": "Pendente"},
    {"ID": "58", "Fase": "Pré Go Live", "Macro Processo": "Suprimentos", "Responsabilidade": "Cliente", "Responsável": "Almoxarifado", "Tarefa": "Devoluções via sistema MV", "Predecessora": "57", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "59", "Fase": "Pós Go Live", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Enfermagem", "Tarefa": "Monitorar prescrições manuais", "Predecessora": "58", "Duração Prevista": 2, "Status": "Pendente"},
    {"ID": "60", "Fase": "Simulação", "Macro Processo": "Assistencial", "Responsabilidade": "Cliente", "Responsável": "Centro Cirúrgico", "Tarefa": "Confirmar cirurgias", "Predecessora": "59", "Duração Prevista": 2, "Status": "Pendente"}
]

# --- INTERFACE ---
st.title("🏥 Dashboard de Cutover Hospitalar")

with st.sidebar:
    st.header("📋 Parâmetros do Projeto")
    projeto = st.text_input("Nome do Projeto", "Implantação MV Hospitalar")
    gp = st.text_input("Gerente de Projetos", "Admin")
    data_inicio = st.date_input("Início do Cronograma", datetime.now(), format="DD/MM/YYYY")
    tolerancia = st.number_input("Tolerância (Dias de Desvio)", min_value=0, value=3)
    
    st.divider()
    st.header("🔍 Filtros Operacionais")
    df_raw = pd.DataFrame(tasks_data)
    f_resp = st.multiselect("Responsabilidade", df_raw['Responsabilidade'].unique(), default=df_raw['Responsabilidade'].unique())
    f_macro = st.multiselect("Macro Processo", df_raw['Macro Processo'].unique(), default=df_raw['Macro Processo'].unique())

# --- PROCESSAMENTO ---
start_dt = datetime.combine(data_inicio, datetime.min.time())
df_full = calculate_schedule(df_raw, start_dt, tolerancia)

# Aplicação dos filtros
df_filtered = df_full[
    (df_full['Responsabilidade'].isin(f_resp)) & 
    (df_full['Macro Processo'].isin(f_macro))
]

# --- PAINEL DE MÉTRICAS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total de Atividades", len(df_filtered))
m2.metric("Pendente/Em Andamento", len(df_filtered[df_filtered['Status'] != 'Concluído']))
m3.metric("Fim Previsto", df_filtered['Data Fim'].max().strftime('%d/%m/%Y'))
m4.metric("Data Limite (Risco)", df_filtered['Data Limite'].max().strftime('%d/%m/%Y'))

st.divider()

# --- VISUALIZAÇÃO GANTT ---
st.subheader("🖼️ Visão Visual do Cronograma")
if not df_filtered.empty:
    fig = px.timeline(
        df_filtered, 
        x_start="Data Início", 
        x_end="Data Fim", 
        y="Tarefa", 
        color="Macro Processo",
        hover_data=["ID", "Responsável", "Status", "Data Limite"],
        labels={"Tarefa": "Atividade"}
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    fig.update_layout(height=700, xaxis_title="Linha do Tempo")
    st.plotly_chart(fig, use_container_width=True)

# --- TABELA DE CONTROLE ---
st.subheader("📑 Tabela de Controle de Execução")
df_display = df_filtered.copy()
for col in ['Data Início', 'Data Fim', 'Data Limite']:
    df_display[col] = df_display[col].dt.strftime('%d/%m/%Y')

st.dataframe(
    df_display[['ID', 'Status', 'Fase', 'Macro Processo', 'Tarefa', 'Responsabilidade', 'Responsável', 'Duração Prevista', 'Data Início', 'Data Fim', 'Data Limite']],
    use_container_width=True,
    hide_index=True
)

st.info(f"Projeto: {projeto} | GP: {gp} | Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
