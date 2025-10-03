import streamlit as st
import pandas as pd
import requests
import altair as alt

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
    st.image("acuimayo_logo.png", width=200)

with col2:
    st.markdown("<h2 style='text-align: center; color: #004080;'>🌊 PicoHidroelectrica - Ingeniería Mecatrónica<br>Acuimayo (Sibundoy, Putumayo)</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #333;'>Universidad Mariana</h4>", unsafe_allow_html=True)

with col3:
    st.image("acuimayo_logo.png", width=200)  # Ejemplo logo Acuimayo

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
