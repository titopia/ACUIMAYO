import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.graph_objects as go
from datetime import datetime

# -------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -------------------------------
st.set_page_config(
    page_title="Picohidroelectrica - Ingeniería Mecatrónica Acuimayo",
    page_icon="⚡",
    layout="wide"
)

# Encabezado con logos
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image("um_logo.png", width=100)
with col2:
    st.markdown(
        "<h2 style='text-align:center;'>Picohidroelectrica Ingeniería Mecatrónica - Acuimayo Universidad Mariana</h2>",
        unsafe_allow_html=True
    )
with col3:
    st.image("acuimayo_logo.png", width=100)

st.write("---")

# -------------------------------
# FUNCIÓN PARA CARGAR DATOS
# -------------------------------
def cargar_datos_thingspeak(channel_id, api_key, results=100):
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}&results={results}"
    response = requests.get(url)
    data = response.json()

    if "feeds" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["feeds"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df

# -------------------------------
# FUNCIÓN PARA MOSTRAR GRÁFICOS
# -------------------------------
def mostrar_grafico(df, campo, nombre, unidad, color="blue"):
    if campo not in df.columns:
        st.warning(f"No hay datos para {nombre}")
        return

    df[campo] = pd.to_numeric(df[campo], errors="coerce")

    if df[campo].isna().all():
        st.warning(f"Datos no válidos en {nombre}")
        return

    # Último valor
    valor_actual = df[campo].iloc[-1]

    # Métrica
    st.metric(label=f"{nombre} actual", value=f"{valor_actual:.2f} {unidad}")

    # Gráfico con Altair
    chart = alt.Chart(df).mark_line(color=color).encode(
        x="created_at:T",
        y=alt.Y(campo, title=f"{nombre} ({unidad})")
    ).properties(
        width="container",
        height=300
    )

    st.altair_chart(chart, use_container_width=True)

# -------------------------------
# FUNCIÓN PARA GAUGE (Plotly)
# -------------------------------
def mostrar_gauge(valor, nombre, unidad, min_val=0, max_val=100, color="blue"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': f"{nombre} ({unidad})"},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color},
            'borderwidth': 2,
            'bordercolor': "gray"
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# CARGA DE DATOS
# -------------------------------
CHANNEL_ID = "3099319"   # tu canal en ThingSpeak
API_KEY = "33IXOBQJG1S9KVJY"  # tu API KEY de solo lectura
df = cargar_datos_thingspeak(CHANNEL_ID, API_KEY, results=200)

# -------------------------------
# PESTAÑAS
# -------------------------------
tabs = st.tabs(["🌡️ Temperatura", "💧 Humedad", "⚡ Voltaje", "🔌 Corriente", "💡 Potencia", "🔋 Energía", "📜 Historial"])

with tabs[0]:
    mostrar_grafico(df, "field1", "Temperatura", "°C", color="red")

with tabs[1]:
    mostrar_grafico(df, "field2", "Humedad", "%", color="green")

with tabs[2]:
    if "field3" in df.columns:
        df["field3"] = pd.to_numeric(df["field3"], errors="coerce")
        valor = df["field3"].iloc[-1]
        st.metric("Voltaje actual", f"{valor:.2f} V")
        mostrar_gauge(valor, "Voltaje", "V", min_val=0, max_val=50, color="orange")

with tabs[3]:
    if "field4" in df.columns:
        df["field4"] = pd.to_numeric(df["field4"], errors="coerce")
        valor = df["field4"].iloc[-1]
        st.metric("Corriente actual", f"{valor:.2f} A")
        mostrar_gauge(valor, "Corriente", "A", min_val=0, max_val=10, color="purple")

with tabs[4]:
    mostrar_grafico(df, "field5", "Potencia", "W", color="blue")

with tabs[5]:
    mostrar_grafico(df, "field6", "Energía", "Wh", color="brown")

with tabs[6]:
    st.subheader("📜 Historial de datos")
    st.dataframe(df)
    # Botón para descargar
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar historial CSV", data=csv, file_name="historial_acuimayo.csv", mime="text/csv")

