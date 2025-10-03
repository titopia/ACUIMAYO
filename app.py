import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# ===== CONFIGURACIÓN =====
CHANNEL_ID = "3099319"   # tu canal ThingSpeak
READ_API_KEY = "33IXOBQJG1S9KVJY"
N_RESULTS = 100

# ===== AUTO REFRESH =====
st_autorefresh = st.experimental_autorefresh(interval=30 * 1000, limit=None, key="refresh")

# ===== CABECERA CON LOGOS =====
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/88/Logo_Universidad_Mariana.png", width=120)

with col2:
    st.markdown("<h2 style='text-align: center; color: #003366;'>🌊 PicoHidroelectrica - Ingeniería Mecatrónica</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Proyecto en la piscicultura <b>Acuimayo (Sibundoy, Putumayo)</b></h4>", unsafe_allow_html=True)

with col3:
    st.image("https://i.ibb.co/8mQyMz2/acuimayo-logo.png", width=120)  # Cambia por tu logo oficial

# ===== FUNCIÓN PARA OBTENER DATOS =====
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

# ===== DASHBOARD =====
df = get_data()

if not df.empty:
    tabs = st.tabs(["⚡ Energía", "🔌 Voltaje", "🔋 Corriente", "🌡️ Temperatura"])

    # -------- TAB ENERGÍA --------
    with tabs[0]:
        st.subheader("⚡ Energía")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_at"], y=df["field1"], mode="lines+markers", name="Energía"))
        fig.update_layout(title="Energía generada", xaxis_title="Tiempo", yaxis_title="Energía (Wh)")
        st.plotly_chart(fig, use_container_width=True)

    # -------- TAB VOLTAJE --------
    with tabs[1]:
        st.subheader("🔌 Voltaje")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_at"], y=df["field2"], mode="lines+markers", name="Voltaje", line=dict(color="blue")))
        fig.update_layout(title="Voltaje generado", xaxis_title="Tiempo", yaxis_title="Voltaje (V)")
        st.plotly_chart(fig, use_container_width=True)

    # -------- TAB CORRIENTE --------
    with tabs[2]:
        st.subheader("🔋 Corriente")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_at"], y=df["field3"], mode="lines+markers", name="Corriente", line=dict(color="green")))
        fig.update_layout(title="Corriente generada", xaxis_title="Tiempo", yaxis_title="Corriente (A)")
        st.plotly_chart(fig, use_container_width=True)

    # -------- TAB TEMPERATURA --------
    with tabs[3]:
        st.subheader("🌡️ Temperatura")
        temp_actual = df["field4"].iloc[-1]

        # Gadget tipo velocímetro
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=temp_actual,
            title={'text': "Temperatura Agua (°C)"},
            gauge={
                'axis': {'range': [0, 40]},
                'bar': {'color': "red"},
                'steps': [
                    {'range': [0, 20], 'color': "lightblue"},
                    {'range': [20, 30], 'color': "lightgreen"},
                    {'range': [30, 40], 'color': "orange"}
                ]
            }
        ))
        st.plotly_chart(gauge, use_container_width=True)

        # Histórico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_at"], y=df["field4"], mode="lines+markers", name="Temperatura", line=dict(color="red")))
        fig.update_layout(title="Histórico de Temperatura", xaxis_title="Tiempo", yaxis_title="°C")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No se encontraron datos para mostrar 🚧")
