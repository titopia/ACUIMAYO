import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ------------------------
# Configuración de la página
# ------------------------
st.set_page_config(
    page_title="Picohidroelectrica Ingeniería Mecatrónica - Acuimayo Universidad Mariana",
    layout="wide"
)

# ------------------------
# Encabezado con logos
# ------------------------
col1, col2, col3, col4 = st.columns([1,2,2,1])

with col1:
    st.image("https://www.umariana.edu.co/images/logo-universidad-mariana.png", width=120)

with col2:
    st.markdown("<h3 style='text-align:center;'>Picohidroelectrica</h3>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>Ingeniería Mecatrónica</h4>", unsafe_allow_html=True)

with col3:
    st.markdown("<h4 style='text-align:center;'>Piscicultura Acuimayo</h4>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align:center;'>Sibundoy - Putumayo</h5>", unsafe_allow_html=True)

with col4:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Logo-fish.png/800px-Logo-fish.png", width=100)

st.markdown("---")

# ------------------------
# Autorefresh cada 30s
# ------------------------
st_autorefresh(interval=30 * 1000, key="refresh")

# ------------------------
# Simulación de datos
# ------------------------
df = pd.DataFrame({
    "Tiempo": pd.date_range("2025-10-01", periods=20, freq="H"),
    "Voltaje": np.random.uniform(210, 230, 20),
    "Corriente": np.random.uniform(5, 15, 20),
    "Energia": np.random.randint(50, 150, 20),
    "Temperatura": np.random.uniform(18, 25, 20)
})

# Último valor de temperatura
temp_actual = df["Temperatura"].iloc[-1]

# ------------------------
# Pestañas
# ------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🔌 Voltaje", "🔋 Corriente", "⚡ Energía", "🌡️ Temperatura"])

with tab1:
    chart_v = alt.Chart(df).mark_line(point=True).encode(
        x="Tiempo:T",
        y=alt.Y("Voltaje:Q", title="Voltaje (V)"),
        tooltip=["Tiempo:T", "Voltaje:Q"]
    ).properties(title="Voltaje generado")
    st.altair_chart(chart_v, use_container_width=True)

with tab2:
    chart_c = alt.Chart(df).mark_line(point=True).encode(
        x="Tiempo:T",
        y=alt.Y("Corriente:Q", title="Corriente (A)"),
        tooltip=["Tiempo:T", "Corriente:Q"]
    ).properties(title="Corriente generada")
    st.altair_chart(chart_c, use_container_width=True)

with tab3:
    chart_e = alt.Chart(df).mark_line(point=True).encode(
        x="Tiempo:T",
        y=alt.Y("Energia:Q", title="Energía (kWh)"),
        tooltip=["Tiempo:T", "Energia:Q"]
    ).properties(title="Energía generada")
    st.altair_chart(chart_e, use_container_width=True)

    # Botón para descargar historial
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar historial de datos", csv, "historial_acuimayo.csv", "text/csv")

with tab4:
    st.subheader("Temperatura del agua (°C)")

    # Gadget tipo velocímetro
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=temp_actual,
        title={'text': "Temperatura actual"},
        gauge={'axis': {'range': [0, 40]},
               'bar': {'color': "blue"},
               'steps': [
                   {'range': [0, 20], 'color': "lightblue"},
                   {'range': [20, 30], 'color': "lightgreen"},
                   {'range': [30, 40], 'color': "red"}]}
    ))
    st.plotly_chart(fig, use_container_width=True)

    chart_t = alt.Chart(df).mark_line(point=True).encode(
        x="Tiempo:T",
        y=alt.Y("Temperatura:Q", title="Temperatura (°C)"),
        tooltip=["Tiempo:T", "Temperatura:Q"]
    ).properties(title="Histórico de temperatura")
    st.altair_chart(chart_t, use_container_width=True)
