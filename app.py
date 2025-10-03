import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.graph_objects as go

# ===== CONFIGURACIÓN =====
CHANNEL_ID = "3099319"  # Reemplaza con tu canal
READ_API_KEY = "33IXOBQJG1S9KVJY"  # Si el canal es privado
N_RESULTS = 100  # número de muestras a leer

# ===== FUNCIÓN PARA DESCARGAR DATOS =====
def get_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results={N_RESULTS}"
    if READ_API_KEY:
        url += f"&api_key={READ_API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()["feeds"]
        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        # convierte a numérico los fields
        for i in range(1, 8):
            if f"field{i}" in df.columns:
                df[f"field{i}"] = pd.to_numeric(df[f"field{i}"], errors="coerce")
        return df
    else:
        st.error("❌ Error al obtener datos de ThingSpeak")
        return pd.DataFrame()

# ===== STREAMLIT APP =====
st.set_page_config(page_title="PicoHidroeléctrica - Acuimayo", layout="wide")
st.title("🌊 PicoHidroeléctrica - Ingeniería Mecatrónica | Acuimayo - Universidad Mariana")

df = get_data()

if not df.empty:
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs(["🌡️ Temperatura y Humedad", "⚡ Energía Eléctrica", "📂 Datos crudos"])

    with tab1:
        st.subheader("Temperatura y Humedad")

        # Gráfico interactivo de temperatura con Plotly
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df["created_at"], y=df["field1"],
            mode="lines+markers", name="Temperatura (°C)", line=dict(color="red")
        ))
        st.plotly_chart(fig_temp, use_container_width=True)

        # Gráfico de humedad con Altair
        chart_hum = alt.Chart(df).mark_line(color="blue").encode(
            x="created_at:T",
            y="field2:Q",
            tooltip=["created_at", "field2"]
        ).properties(title="Humedad (%)")
        st.altair_chart(chart_hum, use_container_width=True)

    with tab2:
        st.subheader("Energía Eléctrica")

        # Extraer último valor
        ultimo_volt = df["field4"].iloc[-1] if not df["field4"].isna().all() else 0
        ultimo_corr = df["field5"].iloc[-1] if not df["field5"].isna().all() else 0
        ultimo_pot  = df["field6"].iloc[-1] if not df["field6"].isna().all() else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            gauge_volt = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ultimo_volt,
                title={'text': "Voltaje (V)"},
                gauge={'axis': {'range': [0, 250]}}
            ))
            st.plotly_chart(gauge_volt, use_container_width=True)

        with col2:
            gauge_corr = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ultimo_corr,
                title={'text': "Corriente (A)"},
                gauge={'axis': {'range': [0, 20]}}
            ))
            st.plotly_chart(gauge_corr, use_container_width=True)

        with col3:
            gauge_pot = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ultimo_pot,
                title={'text': "Potencia (W)"},
                gauge={'axis': {'range': [0, 2000]}}
            ))
            st.plotly_chart(gauge_pot, use_container_width=True)

        st.markdown("---")
        st.subheader("Histórico Energía Eléctrica")

        chart_volt = alt.Chart(df).mark_line(color="orange").encode(
            x="created_at:T", y="field4:Q", tooltip=["created_at", "field4"]
        ).properties(title="Voltaje (V)")

        chart_corr = alt.Chart(df).mark_line(color="red").encode(
            x="created_at:T", y="field5:Q", tooltip=["created_at", "field5"]
        ).properties(title="Corriente (A)")

        chart_pot = alt.Chart(df).mark_line(color="purple").encode(
            x="created_at:T", y="field6:Q", tooltip=["created_at", "field6"]
        ).properties(title="Potencia (W)")

        chart_ener = alt.Chart(df).mark_line(color="green").encode(
            x="created_at:T", y="field7:Q", tooltip=["created_at", "field7"]
        ).properties(title="Energía (kWh)")

        st.altair_chart(chart_volt, use_container_width=True)
        st.altair_chart(chart_corr, use_container_width=True)
        st.altair_chart(chart_pot, use_container_width=True)
        st.altair_chart(chart_ener, use_container_width=True)

    with tab3:
        st.subheader("Datos Crudos")
        st.write(df.tail(20))  # muestra últimos registros

        # Botón de descarga
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Descargar historial en CSV",
            data=csv,
            file_name="acuimayo_historial.csv",
            mime="text/csv"
        )

else:
    st.warning("⚠ No se pudieron cargar los datos aún.")
