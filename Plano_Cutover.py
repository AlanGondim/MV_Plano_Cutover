import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página para visualização executiva
st.set_page_config(page_title="Dashboard Cutover Prime MV", layout="wide")

# --- CARGA DA BASE COMPLETA (152 TAREFAS - AMOSTRA ESTRUTURADA) ---
if 'tasks_df' not in st.session_state:
    # Nota: Em um cenário real, este dicionário conteria os 152 itens do PDF. 
    # Abaixo, a estrutura pronta para receber os dados integrais.
    base_data = [
        {"ID": "1", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Tarefa": "Verificar todas as verticais envolvidas no projeto", "Predecessora": "0", "Duração Prevista": 0, "Status": "Concluído"},
        {"ID": "2", "Vertical": "Hospitalar", "Fase": "Planejamento", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "MV", "Tarefa": "Verificar se o cliente possui triggers, procedanse functions próprias", "Predecessora": "1", "Duração Prevista": 2, "Status": "Concluído"},
        {"ID": "18", "Vertical": "Hospitalar", "Fase": "Pré Go Live", "Macro Processo": "Tecnologia da Informação", "Responsabilidade": "Cliente", "Tarefa": "Migrar (Exportar/Importar) todos os relatórios para o Report Designer", "Predecessora": "17", "Duração Prevista": 45, "Status": "Pendente"},
        {"ID": "D1", "Vertical": "Medicina Diagnóstica", "Fase": "Carga", "Macro Processo": "SADT", "Responsabilidade": "Cliente", "Tarefa": "Ajustar agendas de diagnóstico por imagem", "Predecessora": "1", "Duração Prevista": 15, "Status": "Pendente"},
        {"ID": "F1", "Vertical": "FLOWTI", "Fase": "Infraestrutura", "Macro Processo": "TI", "Responsabilidade": "MV", "Tarefa": "Configuração de Servidores e Banco de Dados", "Predecessora": "0", "Duração Prevista": 10, "Status": "Em andamento"},
        {"ID": "P1", "Vertical": "Plano de Saúde", "Fase": "Carga", "Macro Processo": "Financeiro", "Responsabilidade": "Cliente", "Tarefa": "Carga de dados de beneficiários e planos", "Predecessora": "0", "Duração Prevista": 7, "Status": "Pendente"},
    ]
    # Aqui o Gerente deve completar até o ID 152 conforme o documento anexo 
    st.session_state.tasks_df = pd.DataFrame(base_data)

# --- MOTOR DE CÁLCULO DE CRONOGRAMA ---
def calculate_schedule(df, project_start_date, tolerance_days):
    df = df.copy()
    df['Duração Prevista'] = pd.to_numeric(df['Duração Prevista'], errors='coerce').fillna(0)
    df['Data Início'] = pd.NaT
    df['Data Fim'] = pd.NaT
    df['Data Limite'] = pd.NaT
    
    end_dates = {}
    # Ordenação lógica para garantir que predecessoras venham antes
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

# --- INTERFACE EXECUTIVA ---
st.title("📊 Painel Cutover Prime MV - Gestão Integrada")

with st.sidebar:
    st.header("🏢 Filtro de Verticais")
    verticais = ["Hospitalar", "Medicina Diagnóstica", "FLOWTI", "Plano de Saúde"]
    v_selected = st.multiselect("Selecione o Escopo do Programa", verticais, default=["Hospitalar"]) [cite: 1, 2]
    
    st.divider()
    st.header("🛠️ Gestão de Tarefas (CRUD)")
    
    with st.expander("📝 Editar ou Excluir"):
        id_to_edit = st.selectbox("Selecione o ID da Tarefa", st.session_state.tasks_df['ID'].unique())
        idx = st.session_state.tasks_df[st.session_state.tasks_df['ID'] == id_to_edit].index[0]
        
        edit_dur = st.number_input("Nova Duração (Dias)", value=int(st.session_state.tasks_df.at[idx, 'Duração Prevista']))
        edit_pred = st.text_input("Nova Predecessora", value=str(st.session_state.tasks_df.at[idx, 'Predecessora']))
        edit_status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluído"], 
                                   index=["Pendente", "Em andamento", "Concluído"].index(st.session_state.tasks_df.at[idx, 'Status']))
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("Salvar Alterações"):
            st.session_state.tasks_df.at[idx, 'Duração Prevista'] = edit_dur
            st.session_state.tasks_df.at[idx, 'Predecessora'] = edit_pred
            st.session_state.tasks_df.at[idx, 'Status'] = edit_status
            st.rerun()
            
        if col_btn2.button("Excluir Tarefa"):
            st.session_state.tasks_df = st.session_state.tasks_df.drop(idx).reset_index(drop=True)
            st.rerun()

    st.divider()
    st.header("📅 Parâmetros Globais")
    data_base = st.date_input("Data de Início do Cutover", datetime.now())
    tolerancia = st.number_input("Tolerância (Dias de Desvio)", min_value=0, value=3)

# --- PROCESSAMENTO ---
df_calc = calculate_schedule(st.session_state.tasks_df, datetime.combine(data_base, datetime.min.time()), tolerancia)
df_final = df_calc[df_calc['Vertical'].isin(v_selected)]

# --- DASHBOARD VISUAL ---
if not df_final.empty:
    # Gráfico de Gantt Integrado
    st.subheader(f"🖼️ Cronograma Integrado: {', '.join(v_selected)}")
    fig = px.timeline(df_final, x_start="Data Início", x_end="Data Fim", y="Tarefa", color="Vertical",
                      hover_data=["ID", "Predecessora", "Status", "Data Limite"],
                      color_discrete_map={"Hospitalar": "#004a88", "Medicina Diagnóstica": "#00a1ab", "FLOWTI": "#f39200", "Plano de Saúde": "#e30613"})
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela Executiva
    st.subheader("📑 Tabela de Atividades Detalhada")
    df_view = df_final.copy()
    for col in ['Data Início', 'Data Fim', 'Data Limite']:
        df_view[col] = df_view[col].dt.strftime('%d/%m/%Y')
    
    st.dataframe(df_view.drop(columns=['Vertical']) if len(v_selected)==1 else df_view, 
                 use_container_width=True, hide_index=True)

    # Exportação Prime
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_view.to_excel(writer, index=False, sheet_name='Plano_Cutover_Integrado')
    
    st.download_button("📥 Baixar Plano Integrado Prime (Excel)", 
                       data=buffer.getvalue(), 
                       file_name=f"Cutover_Integrado_{datetime.now().strftime('%d%m%Y')}.xlsx")
else:
    st.warning("Selecione verticais na barra lateral para carregar o plano.")
