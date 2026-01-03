import cv2
import os
from fastapi import FastAPI, Response
from ultralytics import YOLO
import threading
import time

# Forzar el uso de UDP para evitar retardos por retransmisión de paquetes perdidos
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

app = FastAPI()

# --- CONFIGURACIÓN ---
MODEL_PATH = "extras/modelo/best.pt"
# Cambiamos al canal 102 (Sub-stream) para mayor fluidez
RTSP_URL = "rtsp://admin:Novat3ch@192.168.1.5:554/Streaming/Channels/102"
model = YOLO(MODEL_PATH)

ultima_imagen = None
datos_estado = {"nivel": 0, "total": 0, "camara": "Buscando..."}

def detectar_mejor_camara():
    print("🔍 Iniciando jerarquía de búsqueda...")

    # 1. Intentar RTSP
    print(f"📡 Probando RTSP (UDP): {RTSP_URL}")
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if cap.isOpened():
        ret, _ = cap.read()
        if ret:
            print("✅ Conexión RTSP establecida.")
            cap.release()
            return RTSP_URL
        cap.release()

    # 2. Intentar USB (1-5)
    for index in range(1, 6):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"✅ Cámara USB detectada: {index}")
            cap.release()
            return index
        cap.release()
    
    # 3. Intentar integrada
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✅ Usando cámara integrada (0).")
        cap.release()
        return 0
    
    return None

def bucle_deteccion(source):
    global ultima_imagen, datos_estado
    
    cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
    
    # Configuraciones críticas para latencia cero
    if isinstance(source, str) and source.startswith("rtsp"):
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # Algunos sistemas requieren "vaciar" el buffer manualmente
    
    datos_estado["camara"] = "Hikvision" if isinstance(source, str) else f"Puerto {source}"

    while True:
        # TRUCO DE LATENCIA: Leer cuadros extras para limpiar el buffer de la red
        # Si el procesamiento es más lento que la cámara, esto evita el lag.
        if isinstance(source, str):
            for _ in range(3): cap.grab() 

        ret, frame = cap.read()
        if not ret:
            print("⚠️ Conexión perdida. Reintentando...")
            cap.release()
            time.sleep(2)
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
            continue

        # Inferencia reduciendo resolución para ganar velocidad
        results = model(frame, conf=0.5, verbose=False, imgsz=640)
        boxes = results[0].boxes
        atentos = 0
        total = len(boxes)

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = model.names[int(box.cls[0])]
            color = (0, 255, 0) if label.lower() in ["atento", "attentive"] else (0, 0, 255)
            if color == (0, 255, 0): atentos += 1
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        nivel = atentos / total if total > 0 else 0
        datos_estado.update({"nivel": nivel, "total": total})

        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        ultima_imagen = buffer.tobytes()

source_detectada = detectar_mejor_camara()
if source_detectada is not None:
    threading.Thread(target=bucle_deteccion, args=(source_detectada,), daemon=True).start()
else:
    print("🛑 ERROR: No se encontró ninguna cámara. Lógica de servidor detenida.")

@app.get("/video")
async def get_video():
    if ultima_imagen is None: return Response(status_code=404)
    return Response(content=ultima_imagen, media_type="image/jpeg")

@app.get("/datos")
async def get_datos():
    return datos_estado

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)