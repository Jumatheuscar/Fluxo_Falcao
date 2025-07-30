import streamlit as st
import pandas as pd
import plotly.express as px

# Título do app
st.set_page_config(page_title="Dashboard Financeiro", layout="centered")
st.title("📊 Dashboard Financeiro - Gastos Mensais")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Faça upload do seu arquivo Excel", type=["xlsx"])
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        # Conversão da coluna 'data' para datetime
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            df.dropna(subset=['data'], inplace=True)  # Remove linhas com datas inválidas
        else:
            st.error("⚠️ A planilha deve conter uma coluna chamada 'data'.")
            st.stop()

        # Validação das outras colunas
        if not {'valor', 'categoria'}.issubset(df.columns):
            st.error("⚠️ A planilha deve conter as colunas: 'data', 'valor' e 'categoria'.")
            st.stop()

        # Filtro por mês
        df['mes'] = df['data'].dt.to_period('M').astype(str)
        meses_disponiveis = df['mes'].unique().tolist()
        mes_selecionado = st.selectbox("Selecione o mês:", sorted(meses_disponiveis, reverse=True))

        # Filtrando os dados do mês selecionado
        df_mes = df[df['mes'] == mes_selecionado]
        df_gastos = df_mes[df_mes['valor'] < 0]

        # Agrupando os gastos por categoria
        df_grouped = df_gastos.groupby('categoria')['valor'].sum().reset_index()

        # Ordena do maior pro menor gasto
        df_grouped = df_grouped.sort_values(by='valor')

        # Exibe os dados e o gráfico
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
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("📁 Faça upload de um arquivo Excel com as colunas: data, valor, categoria.")
