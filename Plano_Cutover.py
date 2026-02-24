import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Plano de Cutover MV", layout="wide")

def calculate_schedule(df, project_start_date):
    df = df.copy()
    # Limpeza e conversão baseada nos dados do PDF 
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
        
        # Se for a primeira tarefa ou a predecessora for '0' 
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

# Dados estruturados conforme o Plano de Cutover anexado 
tasks_data = [
    {"ID": "1", "Fase": "Planejamento", "Tarefa": "Verificar verticais envolvidas", "Predecessora": "0", "Duração Prevista": 0},
    {"ID": "2", "Fase": "Planejamento", "Tarefa": "Verificar triggers e functions próprias", "Predecessora": "1", "Duração Prevista": 2},
    {"ID": "4", "Fase": "Pré Go Live", "Tarefa": "Atualizar a base de CEP", "Predecessora": "2", "Duração Prevista": 2},
    {"ID": "8", "Fase": "Pré Go Live", "Tarefa": "Instalar gerenciadores de impressão (GIM)", "Predecessora": "4", "Duração Prevista": 15},
    {"ID": "10", "Fase": "Pré Go Live", "Tarefa": "Instalar os LAS em todas as máquinas", "Predecessora": "8", "Duração Prevista": 15},
    {"ID": "18", "Fase": "Pré Go Live", "Tarefa": "Migrar relatórios para Report Designer", "Predecessora": "10", "Duração Prevista": 45},
    {"ID": "21", "Fase": "Pré Go Live", "Tarefa": "Testar leitores de códigos de barras", "Predecessora": "18", "Duração Prevista": 6},
    {"ID": "27", "Fase": "Carga", "Tarefa": "Realizar agendamentos ambulatoriais", "Predecessora": "21", "Duração Prevista": 15},
    {"ID": "47", "Fase": "Simulação", "Tarefa": "Testar o fluxo assistencial completo", "Predecessora": "27", "Duração Prevista": 5},
    {"ID": "55", "Fase": "Simulação", "Tarefa": "Backup do banco e configurações", "Predecessora": "47", "Duração Prevista": 1},
]

st.title("🚀 Cronograma de Cutover Hospitalar")

# Painel de Controle
with st.sidebar:
    st.header("📋 Informações do Projeto")
    nome_projeto = st.text_input("Nome do Projeto", value="Implantação MV")
    gerente_projeto = st.text_input("Gerente de Projetos", value="Seu Nome")
    
    # Input formatado dd/mm/aaaa
    data_base = st.date_input("Data de Início (dd/mm/aaaa)", datetime.now(), format="DD/MM/YYYY")
    
    btn_gerar = st.button("Gerar Plano Completo")

if btn_gerar:
    start_dt = datetime.combine(data_base, datetime.min.time())
    df_final = calculate_schedule(pd.DataFrame(tasks_data), start_dt)
    
    st.header(f"Projeto: {nome_projeto}")
    st.subheader(f"Gerente Responsável: {gerente_projeto}")

    # --- GRÁFICO DE GANTT ---
    # O Plotly usa objetos datetime, o formato dd/mm/aaaa aparece no hover
    fig = px.timeline(
        df_final, 
        x_start="Data Início", 
        x_end="Data Fim", 
        y="Tarefa", 
        color="Fase",
        title="Visualização do Caminho Crítico",
        labels={"Tarefa": "Atividade"}
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y") # Formata o eixo X para dd/mm/aaaa
    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DETALHADA ---
    st.subheader("📅 Tabela de Atividades")
    df_display = df_final.copy()
    
    # Formatação das colunas de data para o usuário final
    df_display['Data Início'] = df_display['Data Início'].dt.strftime('%d/%m/%Y')
    df_display['Data Fim'] = df_display['Data Fim'].dt.strftime('%d/%m/%Y')
    
    st.table(df_display[['ID', 'Fase', 'Tarefa', 'Predecessora', 'Duração Prevista', 'Data Início', 'Data Fim']])
