import streamlit as st
import pandas as pd
import plotly.express as px

# URL da planilha do cliente Falcão
url = 'https://docs.google.com/spreadsheets/d/1ATDFQNUeNvXs-kYDtet9ZdFEIdzOJeeaTUNVJEDtn0s/export?format=csv'

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro - Falcão", layout="centered")
st.title("📊 Dashboard Financeiro - Falcão")

# Carregando dados direto do Google Sheets
try:
    df = pd.read_csv(url)

    # Validação das colunas
    if not {'data', 'valor', 'categoria'}.issubset(df.columns):
        st.error("⚠️ A planilha deve conter as colunas: 'data', 'valor' e 'categoria'.")
        st.stop()

    # Conversão de tipos
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

    # Remover linhas inválidas
    df.dropna(subset=['data', 'valor'], inplace=True)

    # Filtro por mês
    df['mes'] = df['data'].dt.to_period('M').astype(str)
    meses_disponiveis = df['mes'].unique().tolist()
    mes_selecionado = st.selectbox("Selecione o mês:", sorted(meses_disponiveis, reverse=True))

    # Filtrar dados do mês
    df_mes = df[df['mes'] == mes_selecionado]
    df_gastos = df_mes[df_mes['valor'] < 0]

    # Agrupar por categoria
    df_grouped = df_gastos.groupby('categoria')['valor'].sum().reset_index()
    df_grouped = df_grouped.sort_values(by='valor')

    # Tabela
    st.subheader(f"Gastos por Categoria - {mes_selecionado}")
    st.dataframe(df_grouped.style.format({"valor": "R$ {:,.2f}"}), use_container_width=True)

    # Gráfico
    fig = px.bar(
        df_grouped,
        x='valor',
        y='categoria',
        orientation='h',
        title='Distribuição de Gastos',
        labels={'valor': 'Valor (R$)', 'categoria': 'Categoria'},
        text='valor',
    )
    fig.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_tickformat="R$,.2f", yaxis_title=None, height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Erro ao carregar ou processar os dados: {e}")
