import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ------------------------
# Configuración
# ------------------------
st.set_page_config(
    page_title="Picohidroelectrica Ingeniería Mecatrónica - Acuimayo Universidad Mariana",
    layout="wide"
)

CHANNEL_ID = "3099319"       # tu canal de ThingSpeak
READ_API_KEY = "33IXOBQJG1S9KVJY"  # tu API key
N_RESULTS = 100              # cantidad de muestras a leer

# ------------------------
# Función para descargar datos desde ThingSpeak
# ------------------------
def get_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results={N_RESULTS}"
    if READ_API_KEY:
        url += f"&api_key={READ_API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()["feeds"]
        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        # convertir a numérico
        for i in range(1, 8):
            if f"field{i}" in df.columns:
                df[f"field{i}"] = pd.to_numeric(df[f"field{i}"], errors="coerce")
        return df
    else:
        st.error("❌ Error al obtener datos de ThingSpeak")
        return pd.DataFrame()

# ------------------------
# Encabezado con logos
# ------------------------
col1, col2, col3, col4 = st.columns([1,2,2,1])

with col1:
    st.image("um_logo.png", width=300)

with col2:
    st.markdown("<h3 style='text-align:center;'>Picohidroelectrica</h3>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>Ingeniería Mecatrónica</h4>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>AUTOR:Titopia</h4>", unsafe_allow_html=True)

with col3:
    st.markdown("<h4 style='text-align:center;'>Piscicultura Acuimayo</h4>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align:center;'>Sibundoy - Putumayo</h5>", unsafe_allow_html=True)

with col4:
    st.image("acuimayo_logo.png", width=100)

st.markdown("---")

# ------------------------
# Autorefresh cada 30s
# ------------------------
st_autorefresh(interval=30 * 1000, key="refresh")

# ------------------------
# Cargar datos
# ------------------------
df = get_data()

if not df.empty:
    # Renombrar campos para claridad
    df = df.rename(columns={
        "created_at": "Tiempo",
        "field1": "Temperatura",
        "field2": "Humedad",
        "field4": "Voltaje",
        "field5": "Corriente",
        "field6": "Potencia",
        "field7": "Energia"
    })

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

        # Descargar historial
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

else:
    st.warning("⚠ No se pudieron cargar datos de ThingSpeak aún.")

