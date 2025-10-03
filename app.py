import streamlit as st
import pandas as pd
import altair as alt
import requests

# ====== CONFIGURACIÓN DE PÁGINA ======
st.set_page_config(page_title="Acuimayo - Monitoreo", layout="wide")

st.title("🐟 Acuimayo - Monitoreo en Tiempo Real")

# ====== DESCARGA DE DATOS DESDE THINGSPEAK ======
CHANNEL_ID = "TU_CHANNEL_ID"   # reemplazar
READ_API_KEY = "TU_API_KEY"    # reemplazar

url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=100"
response = requests.get(url)
data = response.json()

if "feeds" in data:
    df = pd.DataFrame(data["feeds"])
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"])
    else:
        st.error("⚠ No se recibieron datos del canal.")
        st.stop()
else:
    st.error("⚠ Error al conectar con ThingSpeak.")
    st.stop()

# ====== CREAR PESTAÑAS ======
tabs = st.tabs(["🌡 Temperatura", "💧 Humedad", "🔌 Voltaje", "⚡ Corriente", "🔋 Potencia", "📈 Energía"])

# ====== FUNCIÓN PARA GRAFICAR ======
def mostrar_grafico(df, campo, titulo, color, unidad):
    if campo in df.columns and not df[campo].dropna().empty:
        chart = alt.Chart(df).mark_line(color=color).encode(
            x="created_at:T",
            y=f"{campo}:Q",
            tooltip=["created_at", campo]
        ).properties(title=titulo)
        st.altair_chart(chart, use_container_width=True)
        st.metric(f"{titulo} actual", f"{df[campo].dropna().iloc[-1]:.2f} {unidad}")
    else:
        st.info(f"⚠ No hay datos de {titulo} disponibles.")

# ====== PESTAÑA: TEMPERATURA ======
with tabs[0]:
    mostrar_grafico(df, "field1", "Temperatura", "red", "°C")

# ====== PESTAÑA: HUMEDAD ======
with tabs[1]:
    mostrar_grafico(df, "field2", "Humedad", "blue", "%")

# ====== PESTAÑA: VOLTAJE ======
with tabs[2]:
    mostrar_grafico(df, "field4", "Voltaje", "orange", "V")

# ====== PESTAÑA: CORRIENTE ======
with tabs[3]:
    mostrar_grafico(df, "field5", "Corriente", "red", "A")

# ====== PESTAÑA: POTENCIA ======
with tabs[4]:
    mostrar_grafico(df, "field6", "Potencia", "purple", "W")

# ====== PESTAÑA: ENERGÍA ======
with tabs[5]:
    mostrar_grafico(df, "field7", "Energía", "green", "kWh")
