import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro", layout="centered")
st.title("📊 Dashboard Financeiro - Gastos Mensais")

# Carregando dados do Google Sheets (cliente Falcão)
url = 'https://docs.google.com/spreadsheets/d/1ATDFQNUeNvXs-kYDtet9ZdFEIdzOJeeaTUNVJEDtn0s/export?format=csv'

try:
    df = pd.read_csv(url)

    # Validação de colunas
    if not {'data', 'valor', 'categoria'}.issubset(df.columns):
        st.error("⚠️ A planilha deve conter as colunas: 'data', 'valor' e 'categoria'.")
        st.stop()

    # Conversões
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df.dropna(subset=['data', 'valor'], inplace=True)

    # Criar coluna de mês
    df['mes'] = df['data'].dt.to_period('M').astype(str)
    meses_disponiveis = df['mes'].unique().tolist()
    mes_selecionado = st.selectbox("Selecione o mês:", sorted(meses_disponiveis, reverse=True))

    # Filtrar dados do mês
    df_mes = df[df['mes'] == mes_selecionado]
    df_gastos = df_mes[df_mes['valor'] < 0]

    # Agrupar gastos por categoria
    df_grouped = df_gastos.groupby('categoria')['valor'].sum().reset_index()
    df_grouped = df_grouped.sort_values(by='valor')

    # Tabela
    st.subheader(f"Gastos por Categoria - {mes_selecionado}")
    st.dataframe(df_grouped.style.format({"valor": "R$ {:,.2f}"}), use_container_width=True)

    # Gráfico de barras
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
    st.error(f"❌ Erro ao processar os dados: {e}")
