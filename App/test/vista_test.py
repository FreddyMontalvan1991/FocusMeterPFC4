import streamlit as st
import time
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
# ESTADO
# =============================
if "running" not in st.session_state:
    st.session_state.running = False

# =============================
# CONTROLES
# =============================
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Iniciar monitoreo"):
        st.session_state.running = True

with col2:
    if st.button("⏹️ Detener monitoreo"):
        st.session_state.running = False

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
if st.session_state.running:

    try:
        nivel_resp = requests.get(f"{API_URL}/estimacion_atencion", timeout=1)
        frame_resp = requests.get(f"{API_URL}/frame", timeout=1)

        if frame_resp.status_code == 200:
            mostrar_semaforo(nivel_resp.json()["estimacion_atencion"])
            frame_window.image(frame_resp.content)
        else:
            st.warning("Esperando frame del servidor...")

        time.sleep(0.3)
        st.rerun()

    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.session_state.running = False


"""
import streamlit as st
import time
import requests
import numpy as np

API_URL = "http://localhost:8000"

st.title("📹 Monitoreo en Tiempo Real")


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

        nivel = requests.get(f"{API_URL}/estimacion_atencion").json()["estimacion_atencion"]
        frame = requests.get(f"{API_URL}/frame").json()["frame"]

        if not frame:
            st.error('No hay frames para mostrar!')
            break

        #resp = requests.get(f"{API_URL}/frame")
        mostrar_semaforo(nivel)
        frame_window.image(frame)

        if stop:
            break

    st.info("⏹️ Monitoreo detenido")




import streamlit as st
import requests
import cv2
import numpy as np

API_URL = "http://localhost:8000"

st.title("Monitoreo en Tiempo Real")

start = st.button("Iniciar monitoreo")
stop = st.button("Detener monitoreo")

frame_window = st.image([])
semaforo = st.empty()

def mostrar_semaforo(nivel):
    if nivel >= 0.7:
        semaforo.success("Atención Alta")
    elif nivel >= 0.4:
        semaforo.warning("Atención Media")
    else:
        semaforo.error("Atención Baja")

if start:
    while True:
        nivel = requests.get(f"{API_URL}/estimacion_atencion").json()["estimacion_atencion"]
        mostrar_semaforo(nivel)

        resp = requests.get(f"{API_URL}/frame")
        if resp.content:
            frame = np.frombuffer(resp.content, np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_window.image(frame)

        if stop:
            break
"""
