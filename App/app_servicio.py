from fastapi import FastAPI
from servicio import modelo_atencion
import threading
from fastapi.responses import Response
import cv2

app = FastAPI()

threading.Thread(target=modelo_atencion.ejecutar_modelo, daemon=True).start()

@app.get("/estimacion_atencion")
def ultima_estimacion_atencion():
    return {"estimacion_atencion": modelo_atencion.ultimo_nivel}


@app.get("/frame")
def frame_modelo_atencion():
    frame = modelo_atencion.ultimo_frame

    if frame is None:
        return Response(status_code=204)

    # Convertir numpy array → JPEG en memoria
    success, encoded_image = cv2.imencode(".jpg", frame)

    if not success:
        return Response(status_code=500)

    return Response(
        content=encoded_image.tobytes(),
        media_type="image/jpeg"
    )