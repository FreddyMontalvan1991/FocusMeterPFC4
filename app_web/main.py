# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import threading
from worker import run_worker
from state import latest_frame, estado
import cv2, time

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup():
    threading.Thread(target=run_worker, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/semaforo", response_class=HTMLResponse)
def semaforo(request: Request):
    return templates.TemplateResponse("semaforo.html", {"request": request})

@app.get("/estadisticas", response_class=HTMLResponse)
def estadisticas(request: Request):
    return templates.TemplateResponse("estadisticas.html", {"request": request})

@app.get("/docs", response_class=HTMLResponse)
def docs(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/video")
def video():
    def stream():
        while True:
            if latest_frame is None:
                time.sleep(0.1)
                continue
            _, buf = cv2.imencode(".jpg", latest_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
    return StreamingResponse(stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/estado")
def estado_actual():
    return JSONResponse(estado)
