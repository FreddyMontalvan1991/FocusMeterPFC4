import streamlit as st
import cv2
from ultralytics import YOLO

st.title("📹 Monitoreo en Tiempo Real")

# =============================
# CONFIGURACIÓN
# =============================
MODEL_PATH = "app/extras/best.pt"

# =============================
# CARGAR MODELO
# =============================
@st.cache_resource
def load_model():
    return YOLO(MODEL_PATH)

model = load_model()
class_names = model.names

# =============================
# CONTROLES
# =============================
start = st.button("▶️ Iniciar monitoreo")
stop = st.button("⏹️ Detener monitoreo")

frame_window = st.image([])
semaforo = st.empty()

# =============================
# LÓGICA DE SELECCIÓN AUTOMÁTICA
# =============================
def iniciar_camara():
    # 1. Intentar con la WebCam externa (índice 1)
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) 
    if cap is not None and cap.isOpened():
        ret, _ = cap.read()
        if ret:
            return cap, "Externa (USB)"
        cap.release()

    # 2. Si falla la externa, intentar con la integrada (índice 0)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap is not None and cap.isOpened():
        ret, _ = cap.read()
        if ret:
            return cap, "Integrada"
        cap.release()

    return None, None

# =============================
# MONITOREO
# =============================
if start:
    cap, tipo_camara = iniciar_camara()

    if cap is None:
        st.error("❌ No se detectó ninguna cámara disponible.")
        st.stop()
    
    st.toast(f"✅ Usando cámara {tipo_camara}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Inferencia
        results = model(frame, conf=0.5, verbose=False)
        boxes = results[0].boxes
        atentos = 0
        total = len(boxes)

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            etiqueta = class_names[cls_id]

            color = (0, 255, 0) if etiqueta.lower() in ["atento", "attentive"] else (0, 0, 255)
            if color == (0, 255, 0): atentos += 1

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{etiqueta}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Semáforo
        nivel = atentos / total if total > 0 else 0
        if nivel >= 0.7: semaforo.success(f"🟢 Atención Alta: {nivel:.0%}")
        elif nivel >= 0.4: semaforo.warning(f"🟡 Atención Media: {nivel:.0%}")
        else: semaforo.error(f"🔴 Atención Baja: {nivel:.0%}")

        # Mostrar imagen
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame_rgb)

        if stop:
            break

    cap.release()
    st.info("⏹️ Monitoreo detenido")