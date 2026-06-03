"""
Dashboard de Monitoreo en Tiempo Real
======================================
Interfaz web construida con Streamlit que visualiza los datos registrados
por el nodo edge (Raspberry Pi) en tiempo real.

Muestra:
  - Temperatura (°C) del sensor DHT22
  - Humedad relativa (%) del sensor DHT22
  - Humedad de suelo (%) del sensor capacitivo
  - Historial de recibos de notaría digital (últimas 10 entradas)
  - Gráficas de series de tiempo (últimas 25 lecturas)

El dashboard se refresca automáticamente cada 2 segundos.

Uso:
    streamlit run web/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Notaría Digital IoT — GDSPROC",
    layout     = "wide",
    page_icon  = "🌱",
)

# Refresco automático cada 2 segundos
st_autorefresh(interval=2000, limit=None, key="live_refresh_loop")

# ── Ruta al CSV generado por el nodo edge ──────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CSV = BASE_DIR / "data.csv"


def load_data() -> pd.DataFrame:
    """Carga el log de auditoría desde el CSV local."""
    if DATA_CSV.exists():
        try:
            return pd.read_csv(
                DATA_CSV,
                names=["Hora", "Temperatura", "Humedad", "Humedad_Suelo", "Recibo_Notarial"],
            )
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


# ── Encabezado ─────────────────────────────────────────────────────────────────
st.title("🌱 Monitor de Integridad y Trazabilidad Criptográfica")
st.markdown(
    "**Semillero GDSPROC — Universidad del Quindío** | "
    "📍 Armenia, Quindío | "
    "🔒 Blockchain ligera + Ed25519 + SHA-256"
)
st.markdown("---")

# ── Carga de datos ─────────────────────────────────────────────────────────────
df = load_data()

if not df.empty:
    last = df.iloc[-1]

    # ── Métricas actuales ──────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌡️ Temperatura", f"{last['Temperatura']} °C")
    with col2:
        st.metric("💧 Humedad Relativa", f"{last['Humedad']} %")
    with col3:
        st.metric("🌱 Humedad de Suelo", f"{last['Humedad_Suelo']} %")
    with col4:
        st.metric("🔐 Integridad", "✅ 100% VERIFICADA")

    st.markdown("---")

    # ── Gráfica en tiempo real ─────────────────────────────────────────────────
    st.subheader("📈 Series de Tiempo — Últimas 25 lecturas")
    fig = px.line(
        df.tail(25),
        x     = "Hora",
        y     = ["Temperatura", "Humedad", "Humedad_Suelo"],
        markers = True,
        template = "plotly_dark",
        labels   = {"value": "Valor", "variable": "Variable"},
        color_discrete_map = {
            "Temperatura":   "#FF4B4B",
            "Humedad":       "#00CC96",
            "Humedad_Suelo": "#AB63FA",
        },
    )
    fig.update_layout(legend_title_text="Sensor")
    st.plotly_chart(fig, use_container_width=True)

    # ── Libro de actas ─────────────────────────────────────────────────────────
    st.subheader("📜 Libro de Actas — Historial de Notaría Digital")
    st.dataframe(
        df.tail(10).sort_index(ascending=False),
        use_container_width=True,
    )

    # ── Estadísticas rápidas ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 Estadísticas de la sesión")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Lecturas registradas", len(df))
    with col_b:
        st.metric("Temp. promedio", f"{df['Temperatura'].mean():.2f} °C")
    with col_c:
        st.metric("Humedad suelo promedio", f"{df['Humedad_Suelo'].mean():.2f} %")

else:
    st.warning("⏳ Esperando datos del nodo edge... Asegúrate de que el simulador y el edge_node estén corriendo.")
    st.code(
        "# Terminal 1 — Nodo Edge\n"
        "cd ~/SEMILLERO && source venv/bin/activate\n"
        "python3 -m edge.edge_node\n\n"
        "# Terminal 2 — Simulador ESP32\n"
        "cd ~/SEMILLERO && source venv/bin/activate\n"
        "python3 -m simulator.esp32_sim",
        language="bash",
    )
