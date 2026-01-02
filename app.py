import streamlit as st
import cv2
from ultralytics import YOLO

st.title("📹 Monitoreo en Tiempo Real")

st.markdown(
    """
    Visualización en tiempo real del nivel de atención estudiantil utilizando
    directamente las predicciones del modelo entrenado.
    """
)

# =============================
# CONFIGURACIÓN
# =============================
MODEL_PATH = "app/extras/best.pt"

# Definimos una función para encontrar la cámara disponible
def get_camera():
    # Intenta primero con el índice 1 (comúnmente la webcam externa)
    # y luego con el 0 (comúnmente la integrada)
    for index in [1, 0]:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # Probamos leer un frame para asegurar que realmente funciona
            ret, _ = cap.read()
            if ret:
                return cap, index
            cap.release()
    return None, None

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
# SEMÁFORO
# =============================
def mostrar_semaforo(nivel):
    if nivel >= 0.7:
        semaforo.success(f"🟢 Atención Alta ({nivel:.2%})")
    elif nivel >= 0.4:
        semaforo.warning(f"🟡 Atención Media ({nivel:.2%})")
    else:
        semaforo.error(f"🔴 Atención Baja ({nivel:.2%})")

# =============================
# MONITOREO
# =============================
if start:
    # Intentar obtener la cámara automáticamente
    cap, selected_index = get_camera()

    if cap is None:
        st.error("❌ No se detectó ninguna cámara (webcam o integrada)")
        st.stop()
    else:
        cam_type = "Externa (USB)" if selected_index == 1 else "Integrada"
        st.toast(f"✅ Usando cámara {cam_type}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.warning("⚠️ Se perdió la conexión con la cámara")
            break

        # ===== INFERENCIA YOLO =====
        results = model(frame, conf=0.5)
        boxes = results[0].boxes

        atentos = 0
        total = len(boxes)

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            etiqueta = class_names[cls_id]

            # Color según clase
            if etiqueta.lower() in ["atento", "attentive"]:
                color = (0, 255, 0)
                atentos += 1
            else:
                color = (0, 0, 255)

            # ===== DIBUJAR CUADRO =====
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                f"{etiqueta} ({conf:.2f})",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        # ===== NIVEL DE ATENCIÓN =====
        nivel_atencion = atentos / total if total > 0 else 0
        mostrar_semaforo(nivel_atencion)

        # ===== MOSTRAR VIDEO =====
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame_rgb)

        # Usamos una clave de sesión o el botón stop para salir
        if stop:
            break

    cap.release()
    st.info("⏹️ Monitoreo detenido")