import streamlit as st
import pandas as pd
import requests
import altair as alt

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
st.title("📊 Dashboard IoT con ThingSpeak + Streamlit")
st.write("Visualización en tiempo real de los datos enviados desde el ESP32")

df = get_data()

if not df.empty:
    st.subheader("Datos recientes")
    st.write(df.tail(5))  # muestra las últimas filas
    
    # --- Temperatura y Humedad ---
    st.subheader("📈 Temperatura y Humedad")
    if "field1" in df.columns:
        chart1 = alt.Chart(df).mark_line().encode(
            x="created_at:T", y="field1:Q", tooltip=["created_at", "field1"]
        ).properties(title="Temperatura (°C)")
        st.altair_chart(chart1, use_container_width=True)
    else:
        st.info("🌡 No hay datos en field1 (Temperatura)")

    if "field2" in df.columns:
        chart2 = alt.Chart(df).mark_line(color="green").encode(
            x="created_at:T", y="field2:Q", tooltip=["created_at", "field2"]
        ).properties(title="Humedad (%)")
        st.altair_chart(chart2, use_container_width=True)
    else:
        st.info("💧 No hay datos en field2 (Humedad)")

    # --- Energía Eléctrica ---
    st.subheader("⚡ Energía Eléctrica")
    if "field4" in df.columns:
        chart3 = alt.Chart(df).mark_line(color="orange").encode(
            x="created_at:T", y="field4:Q", tooltip=["created_at", "field4"]
        ).properties(title="Voltaje (V)")
        st.altair_chart(chart3, use_container_width=True)
    else:
        st.info("⚡ No hay datos en field4 (Voltaje)")

    if "field5" in df.columns:
        chart4 = alt.Chart(df).mark_line(color="red").encode(
            x="created_at:T", y="field5:Q", tooltip=["created_at", "field5"]
        ).properties(title="Corriente (A)")
        st.altair_chart(chart4, use_container_width=True)
    else:
        st.info("🔌 No hay datos en field5 (Corriente)")

    if "field6" in df.columns:
        chart5 = alt.Chart(df).mark_line(color="purple").encode(
            x="created_at:T", y="field6:Q", tooltip=["created_at", "field6"]
        ).properties(title="Potencia (W)")
        st.altair_chart(chart5, use_container_width=True)
    else:
        st.info("⚙️ No hay datos en field6 (Potencia)")

    if "field7" in df.columns:
        chart6 = alt.Chart(df).mark_line(color="blue").encode(
            x="created_at:T", y="field7:Q", tooltip=["created_at", "field7"]
        ).properties(title="Energía (kWh)")
        st.altair_chart(chart6, use_container_width=True)
    else:
        st.info("📡 No hay datos en field7 (Energía kWh)")

else:
    st.warning("⚠ No se pudieron cargar los datos aún.")
