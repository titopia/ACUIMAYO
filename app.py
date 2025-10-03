import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ===== CONFIGURACIÓN =====
CHANNEL_ID = "3099319"
READ_API_KEY = "33IXOBQJG1S9KVJY"
N_RESULTS = 100

# ===== AUTOREFRESH cada 30s =====
st_autorefresh(interval=30 * 1000, limit=None, key="refresh")

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
        for i in range(1, 8):
            if f"field{i}" in df.columns:
                df[f"field{i}"] = pd.to_numeric(df[f"field{i}"], errors="coerce")
        return df
    else:
        st.error("❌ Error al obtener datos de ThingSpeak")
        return pd.DataFrame()

# ===== ENCABEZADO CON LOGOS =====
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.image("images/logo_um.png", width=120)
with col2:
    st.title("🌊 PicoHidroelectrica Ingeniería Mecatrónica - Acuimayo")
    st.write("📍 Proyecto en la piscicultura Acuimayo (Sibundoy, Putumayo)")
with col3:
    st.image("images/logo_acuimayo.png", width=120)

# ===== CARGA DE DATOS =====
df = get_data()

if not df.empty:
    tab1, tab2, tab3 = st.tabs(["🌡️ Temperatura", "⚡ Energía Eléctrica", "📊 Datos crudos"])

    # ===== TAB TEMPERATURA =====
    with tab1:
        st.subheader("🌡️ Temperatura (°C)")
        last_temp = df["field1"].dropna().iloc[-1] if not df["field1"].dropna().empty else None

        if last_temp is not None:
            st.metric(label="Temperatura Actual (°C)", value=f"{last_temp:.2f}")
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=last_temp,
                title={'text': "Temperatura (°C)"},
                gauge={'axis': {'range': [0, 50]},
                       'bar': {'color': "red"},
                       'steps': [
                           {'range': [0, 20], 'color': "lightblue"},
                           {'range': [20, 35], 'color': "lightgreen"},
                           {'range': [35, 50], 'color': "lightcoral"}]}
            ))
            st.plotly_chart(gauge, use_container_width=True)

        chart_temp = alt.Chart(df).mark_line(color="red").encode(
            x="created_at:T", y="field1:Q", tooltip=["created_at", "field1"]
        ).properties(title="Histórico de Temperatura")
        st.altair_chart(chart_temp, use_container_width=True)

    # ===== TAB ENERGÍA ELÉCTRICA =====
    with tab2:
        st.subheader("⚡ Monitoreo Eléctrico")

        col1, col2 = st.columns(2)

        # Voltaje
        with col1:
            if "field4" in df.columns:
                last_v = df["field4"].dropna().iloc[-1]
                st.metric("Voltaje (V)", f"{last_v:.2f}")
                gauge_v = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=last_v,
                    title={'text': "Voltaje (V)"},
                    gauge={'axis': {'range': [0, 250]}, 'bar': {'color': "orange"}}
                ))
                st.plotly_chart(gauge_v, use_container_width=True)

        # Corriente
        with col2:
            if "field5" in df.columns:
                last_i = df["field5"].dropna().iloc[-1]
                st.metric("Corriente (A)", f"{last_i:.2f}")
                gauge_i = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=last_i,
                    title={'text': "Corriente (A)"},
                    gauge={'axis': {'range': [0, 50]}, 'bar': {'color': "blue"}}
                ))
                st.plotly_chart(gauge_i, use_container_width=True)

        # Gráficos históricos
        chart_v = alt.Chart(df).mark_line(color="orange").encode(
            x="created_at:T", y="field4:Q", tooltip=["created_at", "field4"]
        ).properties(title="Voltaje (V)")
        chart_i = alt.Chart(df).mark_line(color="blue").encode(
            x="created_at:T", y="field5:Q", tooltip=["created_at", "field5"]
        ).properties(title="Corriente (A)")
        chart_p = alt.Chart(df).mark_line(color="purple").encode(
            x="created_at:T", y="field6:Q", tooltip=["created_at", "field6"]
        ).properties(title="Potencia (W)")
        chart_e = alt.Chart(df).mark_line(color="green").encode(
            x="created_at:T", y="field7:Q", tooltip=["created_at", "field7"]
        ).properties(title="Energía (kWh)")

        st.altair_chart(chart_v, use_container_width=True)
        st.altair_chart(chart_i, use_container_width=True)
        st.altair_chart(chart_p, use_container_width=True)
        st.altair_chart(chart_e, use_container_width=True)

    # ===== TAB DATOS CRUDOS =====
    with tab3:
        st.subheader("📊 Datos crudos recientes")
        st.write(df.tail(20))

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Descargar CSV", csv, "acuimayo_datos.csv", "text/csv")

else:
    st.warning("⚠ No se pudieron cargar los datos aún.")
