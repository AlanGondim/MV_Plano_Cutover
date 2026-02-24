import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Plano de Cutover Profissional", layout="wide")

# Função para calcular o cronograma baseado em predecessoras
def calculate_schedule(df, project_start_date):
    df = df.copy()
    # Tratamento de dados
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(1)
    df['ID'] = df['ID'].astype(str)
    df['Predecessora'] = df['Predecessora'].astype(str).str.strip()
    
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    
    # Dicionário para armazenar a data de término de cada ID calculado
    end_dates = {}

    for index, row in df.iterrows():
        task_id = row['ID']
        pred_id = row['Predecessora']
        duration = int(row['Duração Prevista'])
        
        # Lógica de Predecessora:
        # Se pred for '0', vazio ou igual ao ID (erro comum de OCR), inicia na data do projeto
        if pred_id in ['0', '', task_id] or pred_id not in end_dates:
            current_start = project_start_date
        else:
            # Inicia imediatamente após o término da predecessora
            current_start = end_dates[pred_id]
        
        current_end = current_start + timedelta(days=duration)
        
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Fim'] = current_end
        end_dates[task_id] = current_end
        
    return df

# Dados extraídos do Plano de Cutover (Amostra representativa conforme PDF) 
tasks_data = [
    {"ID": "1", "Fase": "Planejamento", "Tarefa": "Verificar verticais envolvidas", "Predecessora": "0", "Duração Prevista": 1},
    {"ID": "2", "Fase": "Planejamento", "Tarefa": "Verificar triggers e functions próprias", "Predecessora": "1", "Duração Prevista": 2},
    {"ID": "4", "Fase": "Pré Go Live", "Tarefa": "Atualizar a base de CEP", "Predecessora": "2", "Duração Prevista": 2},
    {"ID": "8", "Fase": "Pré Go Live", "Tarefa": "Instalar gerenciadores de impressão (GIM)", "Predecessora": "4", "Duração Prevista": 15},
    {"ID": "10", "Fase": "Pré Go Live", "Tarefa": "Instalar os LAS em todas as máquinas", "Predecessora": "8", "Duração Prevista": 15},
    {"ID": "18", "Fase": "Pré Go Live", "Tarefa": "Migrar relatórios para Report Designer", "Predecessora": "10", "Duração Prevista": 45},
    {"ID": "21", "Fase": "Pré Go Live", "Tarefa": "Testar leitores de códigos de barras", "Predecessora": "18", "Duração Prevista": 6},
    {"ID": "27", "Fase": "Carga", "Tarefa": "Realizar agendamentos ambulatoriais", "Predecessora": "21", "Duração Prevista": 15},
    {"ID": "47", "Fase": "Simulação", "Tarefa": "Testar o fluxo assistencial completo", "Predecessora": "27", "Duração Prevista": 5},
    {"ID": "50", "Fase": "Simulação", "Tarefa": "Refazer documentos em OCX no Editor", "Predecessora": "47", "Duração Prevista": 45},
    {"ID": "55", "Fase": "Simulação", "Tarefa": "Backup do banco e configurações testadas", "Predecessora": "50", "Duração Prevista": 1},
]

# Interface Streamlit
st.title("📊 Gestão Visual de Cutover")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nome_projeto = st.text_input("Nome do Projeto", value="Migração MV Hospitalar")
        gerente_projeto = st.text_input("Gerente de Projetos", value="João Silva")
    with col2:
        data_base = st.date_input("Data Inicial da Primeira Tarefa", datetime.now())
        btn_gerar = st.button("🚀 Gerar Cronograma e Gantt")

if btn_gerar:
    # Processamento
    df_base = pd.DataFrame(tasks_data)
    start_dt = datetime.combine(data_base, datetime.min.time())
    df_final = calculate_schedule(df_base, start_dt)
    
    # Cabeçalho do Relatório
    st.divider()
    st.markdown(f"### 📋 Projeto: {nome_projeto}")
    st.markdown(f"**Responsável:** {gerente_projeto}")
    
    # --- GRÁFICO DE GANTT ---
    st.subheader("🖼️ Gráfico de Gantt")
    fig = px.timeline(
        df_final, 
        x_start="Data Início", 
        x_end="Data Fim", 
        y="Tarefa", 
        color="Fase",
        hover_data=["ID", "Predecessora"],
        title="Cronograma de Execução"
    )
    fig.update_yaxes(autorange="reversed") # Tarefa 1 no topo
    fig.update_layout(xaxis_title="Período", yaxis_title="Tarefas", height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # --- TABELA DE DADOS ---
    st.subheader("📑 Detalhamento das Atividades")
    df_display = df_final.copy()
    df_display['Data Início'] = df_display['Data Início'].dt.strftime('%d/%m/%Y')
    df_display['Data Fim'] = df_display['Data Fim'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_display, use_container_width=True, hide_index=True)

else:
    st.info("Preencha os dados acima e clique em 'Gerar' para visualizar o plano.")