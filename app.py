import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.graph_objects as go

# ===== CONFIGURACIÓN =====
CHANNEL_ID = "3099319"
READ_API_KEY = "33IXOBQJG1S9KVJY"
N_RESULTS = 500

def get_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results={N_RESULTS}"
    if READ_API_KEY:
        url += f"&api_key={READ_API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()["feeds"]
        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        for i in range(1, 8):
            if f"field{i}" in df.columns:
                df[f"field{i}"] = pd.to_numeric(df[f"field{i}"], errors="coerce")
        return df
    else:
        st.error("❌ Error al obtener datos de ThingSpeak")
        return pd.DataFrame()

# ===== ENCABEZADO =====
col1, col2, col3 = st.columns([1,4,1])

with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Escudo_Universidad_Mariana.svg/1200px-Escudo_Universidad_Mariana.svg.png", width=100)

with col2:
    st.markdown("<h2 style='text-align: center; color: #004080;'>🌊 PicoHidroelectrica - Ingeniería Mecatrónica<br>Acuimayo (Sibundoy, Putumayo)</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #333;'>Universidad Mariana</h4>", unsafe_allow_html=True)

with col3:
    st.image("https://i.imgur.com/4Yp9Z3T.png", width=100)  # Logo ejemplo de Acuimayo

st.markdown("---")

# ===== DASHBOARD =====
df = get_data()

if not df.empty:
    st.subheader("📋 Datos recientes")
    st.write(df.tail(10))

    # Botón descarga CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Descargar historial completo (CSV)",
        data=csv,
        file_name="historial_acuimayo.csv",
        mime="text/csv",
    )

    # ===== GADGETS (Voltaje y Corriente) =====
    st.subheader("⚡ Indicadores en Tiempo Real")
    latest = df.tail(1)
    voltaje = latest["field4"].iloc[0] if "field4" in latest.columns else None
    corriente = latest["field5"].iloc[0] if "field5" in latest.columns else None

    colg1, colg2 = st.columns(2)
    with colg1:
        if voltaje is not None:
            fig_v = go.Figure(go.Indicator(
                mode="gauge+number",
                value=voltaje,
                title={'text': "Voltaje (V)"},
                gauge={'axis': {'range': [0, 250]}, 'bar': {'color': "orange"}}
            ))
            st.plotly_chart(fig_v, use_container_width=True)
        else:
            st.info("⚠ No hay datos de voltaje.")

    with colg2:
        if corriente is not None:
            fig_c = go.Figure(go.Indicator(
                mode="gauge+number",
                value=corriente,
                title={'text': "Corriente (A)"},
                gauge={'axis': {'range': [0, 20]}, 'bar': {'color': "red"}}
            ))
            st.plotly_chart(fig_c, use_container_width=True)
        else:
            st.info("⚠ No hay datos de corriente.")

    # ===== FUNCION PARA GRAFICOS =====
    def plot_line(df, field, color, title, ylabel):
        if field in df.columns and df[field].notna().sum() > 0:
            chart = alt.Chart(df).mark_line(color=color).encode(
                x="created_at:T",
                y=alt.Y(field, title=ylabel),
                tooltip=["created_at", field]
            ).properties(title=title)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info(f"⚠ No hay datos disponibles para {title}")

    # ===== GRAFICOS =====
    st.subheader("📈 Temperatura y Humedad")
    plot_line(df, "field1", "blue", "Temperatura (°C)", "°C")
    plot_line(df, "field2", "green", "Humedad (%)", "%")

    st.subheader("⚡ Energía Eléctrica")
    plot_line(df, "field4", "orange", "Voltaje (V)", "Voltios")
    plot_line(df, "field5", "red", "Corriente (A)", "Amperios")
    plot_line(df, "field6", "purple", "Potencia (W)", "Watts")
    plot_line(df, "field7", "blue", "Energía (kWh)", "kWh")

else:
    st.warning("⚠ No se pudieron cargar los datos aún.")
