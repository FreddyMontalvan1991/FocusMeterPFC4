import streamlit as st
#import time
import requests

API_URL = "http://localhost:8000"

st.title("📹 Monitoreo en Tiempo Real")

st.markdown(
    """
    Visualización en tiempo real del nivel de atención estudiantil utilizando
    directamente las predicciones del modelo entrenado.
    """
)

# =============================
# CONTROLES
# =============================
start = st.button("▶️ Iniciar monitoreo")
stop = st.button("⏹️ Detener monitoreo")

frame_window = st.image([])
semaforo = st.empty()

# =============================
# SEMÁFORO
# =============================
def mostrar_semaforo(nivel):
    if nivel >= 0.7:
        semaforo.success("🟢 Atención Alta")
    elif nivel >= 0.4:
        semaforo.warning("🟡 Atención Media")
    else:
        semaforo.error("🔴 Atención Baja")

# =============================
# MONITOREO
# =============================
if start:

    while True:

        # Nivel de atención (JSON)
        nivel_resp = requests.get(f"{API_URL}/estimacion_atencion")
        nivel = nivel_resp.json()["estimacion_atencion"]

        # Frame (imagen binaria)
        frame_resp = requests.get(f"{API_URL}/frame")

        if frame_resp.status_code != 200:
            st.error("No hay frames para mostrar!")
            break

        mostrar_semaforo(nivel)
        frame_window.image(frame_resp.content)

        # ⏱️ refresco cada 0.3 segundos
        #time.sleep(0.3)

        if stop:
            break

    st.info("⏹️ Monitoreo detenido")
