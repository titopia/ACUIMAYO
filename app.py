import streamlit as st
import pandas as pd
import requests
import altair as alt

# ===== CONFIGURACIÓN =====
CHANNEL_ID = "3099319"  # Reemplaza con tu canal
READ_API_KEY = "33IXOBQJG1S9KVJY"  # Si el canal es privado
N_RESULTS = 500  # número de muestras a leer

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

# ===== ENCABEZADO CON LOGOS =====
col1, col2, col3 = st.columns([1,6,1])
with col1:
    st.image("images/um_logo.png", width=100)  # Logo Universidad Mariana
with col2:
    st.markdown(
        "<h2 style='text-align: center;'>🌊 PicoHidroelectrica - Ingeniería Mecatrónica<br>"
        "Acuimayo (Piscicultura en Sibundoy, Putumayo)<br>Universidad Mariana</h2>",
        unsafe_allow_html=True
    )
with col3:
    st.image("images/acuimayo_logo.png", width=100)  # Logo Acuimayo

st.write("Visualización en tiempo real de los datos enviados desde el ESP32 en la planta de Acuimayo.")

# ===== DATOS =====
df = get_data()

if not df.empty:
    st.subheader("📋 Datos recientes")
    st.write(df.tail(10))  # muestra las últimas filas
    
    # Botón para descargar CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Descargar historial completo (CSV)",
        data=csv,
        file_name="historial_acuimayo.csv",
        mime="text/csv",
    )

    # ===== Gráficas =====
    st.subheader("📈 Temperatura y Humedad")
    chart1 = alt.Chart(df).mark_line().encode(
        x="created_at:T",
        y="field1:Q",
        tooltip=["created_at", "field1"]
    ).properties(title="Temperatura (°C)")
    chart2 = alt.Chart(df).mark_line(color="green").encode(
        x="created_at:T",
        y="field2:Q",
        tooltip=["created_at", "field2"]
    ).properties(title="Humedad (%)")
    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart2, use_container_width=True)

    st.subheader("⚡ Energía Eléctrica")
    chart3 = alt.Chart(df).mark_line(color="orange").encode(
        x="created_at:T",
        y="field4:Q",
        tooltip=["created_at", "field4"]
    ).properties(title="Voltaje (V)")
    chart4 = alt.Chart(df).mark_line(color="red").encode(
        x="created_at:T",
        y="field5:Q",
        tooltip=["created_at", "field5"]
    ).properties(title="Corriente (A)")
    chart5 = alt.Chart(df).mark_line(color="purple").encode(
        x="created_at:T",
        y="field6:Q",
        tooltip=["created_at", "field6"]
    ).properties(title="Potencia (W)")
    chart6 = alt.Chart(df).mark_line(color="blue").encode(
        x="created_at:T",
        y="field7:Q",
        tooltip=["created_at", "field7"]
    ).properties(title="Energía (kWh)")
    
    st.altair_chart(chart3, use_container_width=True)
    st.altair_chart(chart4, use_container_width=True)
    st.altair_chart(chart5, use_container_width=True)
    st.altair_chart(chart6, use_container_width=True)

else:
    st.warning("⚠ No se pudieron cargar los datos aún.")
