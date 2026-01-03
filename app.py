import streamlit as st
import cv2
import threading
from ultralytics import YOLO
import time

# =============================
# PROCESADOR OPTIMIZADO
# =============================
class VideoProcessor:
    def __init__(self, index):
        self.cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        # Reducimos resolución para ganar mucha velocidad y bajar CPU
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.model = YOLO("app/extras/best.pt")
        self.frame = None
        self.nivel_atencion = 0
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.update, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def update(self):
        # Limitamos la cámara a 20-25 FPS (suficiente para monitoreo)
        target_fps = 20 
        frame_time = 1.0 / target_fps
        
        while self.running:
            start_time = time.time()
            
            ret, frame = self.cap.read()
            if not ret: break

            # INFERENCIA (Solo si es necesario)
            results = self.model(frame, conf=0.5, verbose=False)
            
            # Usamos el método más eficiente para anotar
            annotated_frame = results[0].plot()

            # Lógica de atención simplificada
            boxes = results[0].boxes
            total = len(boxes)
            atentos = sum(1 for b in boxes if self.model.names[int(b.cls[0])].lower() in ["atento", "attentive"])
            
            with self.lock:
                self.frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                self.nivel_atencion = atentos / total if total > 0 else 0

            # --- FRENO DE CPU ---
            # Calcula cuánto tiempo dormir para mantener los FPS objetivo
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)

# =============================
# VISTA STREAMLIT OPTIMIZADA
# =============================
@st.cache_resource
def get_processor():
    for idx in [2, 0]:
        test_cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        if test_cap.isOpened():
            test_cap.release()
            return VideoProcessor(idx)
    return None

st.title("📹 Monitoreo Eficiente")
processor = get_processor()

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

col1, col2 = st.columns(2)
if col1.button("▶️ Iniciar"):
    st.session_state.monitoring = True
    processor.start()
if col2.button("⏹️ Detener"):
    st.session_state.monitoring = False
    processor.stop()

frame_window = st.image([])
semaforo = st.empty()

# Loop de visualización con frecuencia controlada
if st.session_state.monitoring:
    while st.session_state.monitoring:
        with processor.lock:
            img = processor.frame
            nivel = processor.nivel_atencion

        if img is not None:
            frame_window.image(img, use_container_width=True)
            # Actualizar semáforo solo si hay cambio significativo (opcional)
            if nivel >= 0.7: semaforo.success(f"🟢 Nivel: {nivel:.0%}")
            elif nivel >= 0.4: semaforo.warning(f"🟡 Nivel: {nivel:.0%}")
            else: semaforo.error(f"🔴 Nivel: {nivel:.0%}")
        
        # EL SECRETO: Dormir el hilo de Streamlit
        # No necesitamos actualizar la web a más de 15-20 veces por segundo
        time.sleep(0.05)