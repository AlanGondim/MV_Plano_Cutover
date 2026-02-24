import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Plano de Cutover MV", layout="wide")

def calculate_schedule(df, project_start_date):
    df = df.copy()
    # Limpeza e conversão de dados
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(1)
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Predecessora'] = df['Predecessora'].astype(str).str.strip()
    
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    
    end_dates = {}

    for index, row in df.iterrows():
        task_id = row['ID']
        pred_id = row['Predecessora']
        duration = int(row['Duração Prevista'])
        
        # Lógica de encadeamento: Se for ID 1 ou sem predecessora válida, inicia na data base
        if pred_id in ['0', '', task_id] or pred_id not in end_dates:
            current_start = project_start_date
        else:
            current_start = end_dates[pred_id]
        
        # Cálculo: Data Fim = Início + Duração
        current_end = current_start + timedelta(days=duration)
        
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Fim'] = current_end
        end_dates[task_id] = current_end
        
    return df

# Dados estruturados extraídos integralmente do Plano de Cutover Hospitalar 
tasks_data = [
    {"ID": "1", "Fase": "Planejamento", "Tarefa": "Verificar verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0},
    {"ID": "2", "Fase": "Planejamento", "Tarefa": "Verificar triggers e functions próprias", "Predecessora": "1", "Duração Prevista": 2},
    {"ID": "3", "Fase": "Pré Go Live", "Tarefa": "Atualizar a versão do sistema", "Predecessora": "2", "Duração Prevista": 2},
    {"ID": "4", "Fase": "Pré Go Live", "Tarefa": "Atualizar a base de CEP", "Predecessora": "3", "Duração Prevista": 2},
    {"ID": "5", "Fase": "Pré Go Live", "Tarefa": "Validar todas as integrações", "Predecessora": "4", "Duração Prevista": 10},
    {"ID": "6", "Fase": "Pré Go Live", "Tarefa": "Validar funcionalidades multiempresa", "Predecessora": "5", "Duração Prevista": 2},
    {"ID": "7", "Fase": "Pré Go Live", "Tarefa": "Validar autorização hospitalar e convênios", "Predecessora": "6", "Duração Prevista": 6},
    {"ID": "8", "Fase": "Pré Go Live", "Tarefa": "Instalar gerenciadores de impressão (GIM)", "Predecessora": "7", "Duração Prevista": 15},
    {"ID": "9", "Fase": "Pré Go Live", "Tarefa": "Instalar máquinas na rede", "Predecessora": "8", "Duração Prevista": 15},
    {"ID": "10", "Fase": "Pré Go Live", "Tarefa": "Instalar os LAS em todas as máquinas", "Predecessora": "9", "Duração Prevista": 15},
    {"ID": "11", "Fase": "Pré Go Live", "Tarefa": "Instalar o Cent Browser em todas as máquinas", "Predecessora": "10", "Duração Prevista": 15},
    {"ID": "12", "Fase": "Pré Go Live", "Tarefa": "Preparar ferramenta de acesso remoto", "Predecessora": "11", "Duração Prevista": 10},
    {"ID": "13", "Fase": "Pré Go Live", "Tarefa": "Revisar tickets impeditivos", "Predecessora": "12", "Duração Prevista": 0},
    {"ID": "14", "Fase": "Pré Go Live", "Tarefa": "Divulgar lista de login dos usuários", "Predecessora": "13", "Duração Prevista": 1},
    {"ID": "15", "Fase": "Pré Go Live", "Tarefa": "Validar todos os vínculos e usuários", "Predecessora": "14", "Duração Prevista": 2},
    {"ID": "16", "Fase": "Pré Go Live", "Tarefa": "Verificar relação Usuário x Prestador", "Predecessora": "15", "Duração Prevista": 5},
    {"ID": "17", "Fase": "Pré Go Live", "Tarefa": "Testar impressões de fichas e guias SADT", "Predecessora": "16", "Duração Prevista": 10},
    {"ID": "18", "Fase": "Pré Go Live", "Tarefa": "Migrar relatórios para Report Designer", "Predecessora": "17", "Duração Prevista": 45},
    {"ID": "19", "Fase": "Pré Go Live", "Tarefa": "Testar impressão de documentos de prontuário", "Predecessora": "18", "Duração Prevista": 10},
    {"ID": "20", "Fase": "Pré Go Live", "Tarefa": "Testar etiquetas de todos os setores", "Predecessora": "19", "Duração Prevista": 10},
    {"ID": "21", "Fase": "Pré Go Live", "Tarefa": "Testar leitores de código de barras", "Predecessora": "20", "Duração Prevista": 6},
    {"ID": "22", "Fase": "Pré Go Live", "Tarefa": "Vincular usuários por unidade de internação", "Predecessora": "21", "Duração Prevista": 10},
    {"ID": "23", "Fase": "Pré Go Live", "Tarefa": "Vincular Usuário x Prestador para PEP", "Predecessora": "22", "Duração Prevista": 10},
    {"ID": "24", "Fase": "Pré Go Live", "Tarefa": "Configurar escalas de Agendamento (SCMA)", "Predecessora": "23", "Duração Prevista": 30},
    {"ID": "25", "Fase": "Pré Go Live", "Tarefa": "Levantamento de internações sistema atual", "Predecessora": "24", "Duração Prevista": 5},
    {"ID": "26", "Fase": "Pré Go Live", "Tarefa": "Levantamento de agendamentos cirúrgicos", "Predecessora": "25", "Duração Prevista": 5},
    {"ID": "27", "Fase": "Carga", "Tarefa": "Realizar agendamentos ambulatoriais", "Predecessora": "26", "Duração Prevista": 15},
    {"ID": "28", "Fase": "Carga", "Tarefa": "Realizar agendamentos cirúrgicos", "Predecessora": "27", "Duração Prevista": 15},
    {"ID": "29", "Fase": "Carga", "Tarefa": "Realizar agendamentos de exames", "Predecessora": "28", "Duração Prevista": 15},
    {"ID": "30", "Fase": "Carga", "Tarefa": "Migrar agendas de diagnóstico por imagem", "Predecessora": "29", "Duração Prevista": 15},
    {"ID": "31", "Fase": "Carga", "Tarefa": "Realizar internação dos pacientes", "Predecessora": "30", "Duração Prevista": 2},
    {"ID": "32", "Fase": "Carga", "Tarefa": "Carga de dados financeiros (CP/CR/Saldos)", "Predecessora": "31", "Duração Prevista": 5},
    {"ID": "33", "Fase": "Carga", "Tarefa": "Realizar carga de dados contábeis", "Predecessora": "32", "Duração Prevista": 2},
    {"ID": "34", "Fase": "Pré Go Live", "Tarefa": "Alterar Custo Médio Diário para Mensal", "Predecessora": "33", "Duração Prevista": 5},
    {"ID": "35", "Fase": "Pré Go Live", "Tarefa": "Definir telas de Administradora de Cartão", "Predecessora": "34", "Duração Prevista": 2},
    {"ID": "36", "Fase": "Pré Go Live", "Tarefa": "Unificar processos de Caixa e Tesouraria", "Predecessora": "35", "Duração Prevista": 2},
    {"ID": "37", "Fase": "Pré Go Live", "Tarefa": "Orientar devolução de produtos excedentes", "Predecessora": "36", "Duração Prevista": 5},
    {"ID": "38", "Fase": "Pré Go Live", "Tarefa": "Etiquetar produtos com etiquetas MV", "Predecessora": "37", "Duração Prevista": 10},
    {"ID": "39", "Fase": "Carga", "Tarefa": "Realizar Inventário Geral", "Predecessora": "38", "Duração Prevista": 5},
    {"ID": "40", "Fase": "Pré Go Live", "Tarefa": "Divulgar agenda de multiplicadores", "Predecessora": "39", "Duração Prevista": 2},
    {"ID": "41", "Fase": "Pré Go Live", "Tarefa": "Divulgar agenda do time de migração", "Predecessora": "40", "Duração Prevista": 2},
    {"ID": "42", "Fase": "Pré Go Live", "Tarefa": "Divulgar agenda da consultoria", "Predecessora": "41", "Duração Prevista": 2},
    {"ID": "43", "Fase": "Pré Go Live", "Tarefa": "Validar logins e perfis na simulação", "Predecessora": "42", "Duração Prevista": 2},
    {"ID": "44", "Fase": "Pré Go Live", "Tarefa": "Criar paciente fictício para Produção", "Predecessora": "43", "Duração Prevista": 2},
    {"ID": "45", "Fase": "Planejamento", "Tarefa": "Verificar estações contratadas x real", "Predecessora": "44", "Duração Prevista": 0},
    {"ID": "46", "Fase": "Simulação", "Tarefa": "Testar abertura de atendimentos", "Predecessora": "45", "Duração Prevista": 2},
    {"ID": "47", "Fase": "Simulação", "Tarefa": "Testar fluxo assistencial completo", "Predecessora": "46", "Duração Prevista": 5},
    {"ID": "48", "Fase": "Simulação", "Tarefa": "Ajustar telas descontinuadas PEP", "Predecessora": "47", "Duração Prevista": 5},
    {"ID": "49", "Fase": "Simulação", "Tarefa": "Scripts de ajuste de prescrição", "Predecessora": "48", "Duração Prevista": 2},
    {"ID": "50", "Fase": "Simulação", "Tarefa": "Refazer documentos OCX no Editor", "Predecessora": "49", "Duração Prevista": 45},
    {"ID": "51", "Fase": "Simulação", "Tarefa": "Testar solicitação de exames", "Predecessora": "50", "Duração Prevista": 5},
    {"ID": "52", "Fase": "Simulação", "Tarefa": "Testar solicitações diversas para estoque", "Predecessora": "51", "Duração Prevista": 5},
    {"ID": "53", "Fase": "Simulação", "Tarefa": "Testar fechamento de contas faturamento", "Predecessora": "52", "Duração Prevista": 5},
    {"ID": "54", "Fase": "Simulação", "Tarefa": "Testar caixa (recebimento/estorno)", "Predecessora": "53", "Duração Prevista": 5},
    {"ID": "55", "Fase": "Simulação", "Tarefa": "Backup do banco e configurações testadas", "Predecessora": "54", "Duração Prevista": 1},
    {"ID": "56", "Fase": "Pré Go Live", "Tarefa": "Abrir Centex para avaliação ST", "Predecessora": "55", "Duração Prevista": 0},
    {"ID": "57", "Fase": "Pós Go Live", "Tarefa": "Monitorar relatório de consumo faturamento", "Predecessora": "56", "Duração Prevista": 0},
    {"ID": "58", "Fase": "Pré Go Live", "Tarefa": "Garantir devoluções via sistema MV", "Predecessora": "57", "Duração Prevista": 2},
    {"ID": "59", "Fase": "Pós Go Live", "Tarefa": "Monitorar prescrições manuais", "Predecessora": "58", "Duração Prevista": 2},
    {"ID": "60", "Fase": "Simulação", "Tarefa": "Acompanhar confirmação cirúrgica", "Predecessora": "59", "Duração Prevista": 2},
]

st.title("🚀 Plano de Cutover Hospitalar - MV")

# Barra Lateral de Configurações
with st.sidebar:
    st.header("📋 Gestão do Projeto")
    nome_projeto = st.text_input("Nome do Projeto", value="Migração MV Hospitalar")
    gerente_projeto = st.text_input("Gerente de Projetos", value="Digite seu nome")
    
    # Input de data no formato dd/mm/aaaa
    data_base = st.date_input("Data Inicial (dd/mm/aaaa)", datetime.now(), format="DD/MM/YYYY")
    
    btn_gerar = st.button("🚀 Gerar Cronograma e Gantt")

if btn_gerar:
    # Processamento dos dados
    start_dt = datetime.combine(data_base, datetime.min.time())
    df_final = calculate_schedule(pd.DataFrame(tasks_data), start_dt)
    
    # Exibição do Cabeçalho
    st.markdown(f"### Projeto: {nome_projeto}")
    st.markdown(f"**Responsável:** {gerente_projeto}")
    st.divider()

    # --- GRÁFICO DE GANTT ---
    st.subheader("🖼️ Gráfico de Gantt")
    fig = px.timeline(
        df_final, 
        x_start="Data Início", 
        x_end="Data Fim", 
        y="Tarefa", 
        color="Fase",
        hover_data={"ID": True, "Predecessora": True, "Data Início": "|%d/%m/%Y", "Data Fim": "|%d/%m/%Y"},
        title="Fluxo de Execução do Cutover"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    fig.update_layout(height=800, xaxis_title="Linha do Tempo")
    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DETALHADA ---
    st.subheader("📅 Tabela de Atividades Detalhada")
    df_display = df_final.copy()
    
    # Formatação das colunas de data para o padrão dd/mm/aaaa
    df_display['Data Início'] = df_display['Data Início'].dt.strftime('%d/%m/%Y')
    df_display['Data Fim'] = df_display['Data Fim'].dt.strftime('%d/%m/%Y')
    
    # Exibe a tabela organizada
    st.dataframe(
        df_display[['ID', 'Fase', 'Tarefa', 'Predecessora', 'Duração Prevista', 'Data Início', 'Data Fim']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Ajuste as informações na barra lateral e clique em 'Gerar' para visualizar o plano completo.")

