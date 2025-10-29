import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard de Libros", layout="wide")
st.title("Tus Books que has escrapeao quillo 🐳💨")
st.markdown("Aqui ehtan mirateloh!")

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    return df

df = load_data()

st.sidebar.header("Filtros")
ratings = sorted(df["Rating"].unique())
rating_filter = st.sidebar.multiselect("Selecciona uno o varios ratings:", options=ratings, default=ratings)
min_price = float(df["Precio"].min())
max_price = float(df["Precio"].max())
price_range = st.sidebar.slider("Selecciona un rango de precios (£):", min_value=min_price, max_value=max_price, value=(min_price, max_price))

filtered_df = df[(df["Rating"].isin(rating_filter)) & (df["Precio"].between(price_range[0], price_range[1]))]

st.subheader("Datos filtrados")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("Distribución de precios por rating")
chart = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x=alt.X("Precio", bin=alt.Bin(maxbins=20), title="Precio (£)"),
        y="count()",
        color="Rating:N",
        tooltip=["count()", "Rating:N"]
    )
    .interactive()
)
st.altair_chart(chart, use_container_width=True)

st.subheader("Precio promedio por Rating")
avg_price = (
    filtered_df.groupby("Rating")["Precio"]
    .mean()
    .reset_index()
    .sort_values("Precio", ascending=False)
)
st.bar_chart(avg_price.set_index("Rating"))

st.sidebar.markdown("Descargar datos filtrados")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(label="Descargar CSV filtrado", data=csv, file_name="libros_filtrados.csv", mime="text/csv")
