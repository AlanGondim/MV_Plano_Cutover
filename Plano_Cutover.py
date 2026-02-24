import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from graphviz import Digraph
import io

# Configuração da página
st.set_page_config(page_title="Gestão de Cutover Integrado Prime", layout="wide")

# --- 1. BASE DE DADOS INTEGRAL (Carga das 152 Tarefas) ---
if 'tasks_df' not in st.session_state:
    # Estrutura baseada nos documentos fornecidos 
    # Representação das tarefas mapeadas (Expandir para a lista total de 152)
    base_data = [
        {"ID": "1", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "Equipe MV", "Tarefa": "Verificar todas as verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
        {"ID": "2", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Responsável": "DBA MV", "Tarefa": "Verificar se o cliente possui triggers, procedanse functions próprias", "Predecessora": "1", "Duração Prevista": 2, "Status": "Concluído"},
        {"ID": "3", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Atualizar a versão do sistema", "Predecessora": "2", "Duração Prevista": 2, "Status": "Em andamento"},
        {"ID": "18", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Migrar relatórios para o Report Designer", "Predecessora": "17", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "50", "Vertical": "Hospitalar", "Fase": "Simulação", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Responsável": "TI Local", "Tarefa": "Refazer os documentos em OCX no Editor", "Predecessora": "49", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "D1", "Vertical": "Medicina Diagnóstica", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Responsável": "Radiologia", "Tarefa": "Ajustar agendas de diagnóstico por imagem", "Predecessora": "1", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "F1", "Vertical": "FLOWTI", "Fase": "Infraestrutura", "Macro Processo": "TI", "Responsabilidade": "MV", "Responsável": "Infra", "Tarefa": "Configuração de Servidores", "Predecessora": "0", "Duração Prevista": 10, "Status": "Pendente"},
        {"ID": "P1", "Vertical": "Plano de Saúde", "Fase": "Carga", "Macro Processo": "Financeiro", "Responsabilidade": "Cliente", "Responsável": "Financeiro", "Tarefa": "Carga de Beneficiários", "Predecessora": "0", "Duração Prevista": 7, "Status": "Pendente"}
    ]
    st.session_state.tasks_df = pd.DataFrame(base_data)

# --- 2. MOTOR DE CÁLCULO (CPM E DATAS) ---
def calculate_prime_schedule(df, start_date, tolerance):
    df = df.copy()
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista']).fillna(0)
    df['Data Início'] = pd.NaT
    df['Data Término'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    end_dates = {}
    df = df.sort_values(by=['ID']) 

    for index, row in df.iterrows():
        t_id, pred_id = str(row['ID']), str(row['Predecessora'])
        duration = int(row['Duração Prevista'])
        
        current_start = end_dates[pred_id] if pred_id in end_dates else start_date
        current_end = current_start + timedelta(days=duration)
        limit_date = current_end + timedelta(days=tolerance)
        
        df.at[index, 'Data Início'] = current_start
        df.at[index, 'Data Término'] = current_end
        df.at[index, 'Data Limite'] = limit_date
        df.at[index, 'Is_Critical'] = duration > 10 # Exemplo de Caminho Crítico visual
        end_dates[t_id] = current_end
    return df

# --- 3. INTERFACE E DASHBOARD ---
st.title("🚀 Cutover Integrado Prime MV")

with st.sidebar:
    st.header("⚙️ Configurações do Programa")
    verticais = ["Hospitalar", "Medicina Diagnóstica", "FLOWTI", "Plano de Saúde"]
    v_selected = st.multiselect("Selecione as Verticais", verticais, default=["Hospitalar"])
    
    data_projeto = st.date_input("Início do Cutover", datetime.now())
    tolerancia = st.number_input("Tolerância (Dias)", min_value=0, value=3)
    
    st.divider()
    st.header("🛠️ Gerenciar Linhas")
    with st.expander("🆕 Nova / Editar Tarefa"):
        id_task = st.text_input("ID da Tarefa")
        desc_task = st.text_input("Descrição")
        dur_task = st.number_input("Duração", 0)
        pred_task = st.text_input("Predecessora (ID)", "0")
        stat_task = st.selectbox("Status", ["Pendente", "Em andamento", "Concluído"])
        
        if st.button("Salvar Tarefa"):
            new_row = {"ID": id_task, "Vertical": v_selected[0] if v_selected else "Hospitalar", 
                       "Tarefa": desc_task, "Predecessora": pred_task, "Duração Prevista": dur_task, "Status": stat_task}
            st.session_state.tasks_df = pd.concat([st.session_state.tasks_df, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

# --- 4. PROCESSAMENTO ---
df_calc = calculate_prime_schedule(st.session_state.tasks_df, datetime.combine(data_projeto, datetime.min.time()), tolerancia)
df_final = df_calc[df_calc['Vertical'].isin(v_selected)]

# --- 5. VISUALIZAÇÕES PRIME ---
tab1, tab2, tab3 = st.tabs(["📊 Planilha de Controle", "📅 Gantt & Caminho Crítico", "🕸️ Diagrama PERT"])

with tab1:
    st.subheader("Controle de Execução")
    df_display = df_final.copy()
    for col in ['Data Início', 'Data Término', 'Data Limite']:
        df_display[col] = df_display[col].dt.strftime('%d/%m/%Y')
    
    st.data_editor(df_display, use_container_width=True, hide_index=True)
    
    # BOTÃO EXCEL PRIME
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_display.to_excel(writer, index=False, sheet_name='Plano_Cutover')
    
    st.download_button(
        label="📥 Gerar Cronograma em Excel",
        data=buffer.getvalue(),
        file_name=f"Cronograma_Cutover_{datetime.now().strftime('%d%m%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with tab2:
    st.subheader("Cronograma Visual")
    
    fig = px.timeline(df_final, x_start="Data Início", x_end="Data Término", y="Tarefa", color="Status",
                      hover_data=["ID", "Responsável", "Data Limite"])
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Rede de Dependências (PERT)")
    
    dot = Digraph(comment='PERT', graph_attr={'rankdir':'LR'})
    for _, row in df_final.iterrows():
        color = 'red' if row['Is_Critical'] else 'black'
        dot.node(row['ID'], f"{row['ID']}\n{row['Tarefa']}", color=color)
        if row['Predecessora'] != '0' and row['Predecessora'] in df_final['ID'].values:
            dot.edge(row['Predecessora'], row['ID'])
    st.graphviz_chart(dot)
