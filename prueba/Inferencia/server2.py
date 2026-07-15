from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
import keras
from ultralytics import YOLO
import shutil
import os

app = FastAPI()

# Cargar el modelo y configurar MediaPipe
model = keras.models.load_model("C:\\EV\\proyIA\\lstm20-final2.h5")

fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_path = "C:\\EV\\PROYECTO\\prueba\\video_procesado.mp4"
connections = [
    [0, 1], [0, 2], [1, 3], [2, 4], 
    [5, 6], [5, 7], [6, 8], [7, 9], 
    [8, 10], [5, 11], [6, 12], [11, 12], 
    [11, 13], [12, 14], [13, 15], [14, 16]
]
lm_list = []
valor=None
message=""
solution=""
def make_landmark_timestep(results):
    #c_lm = []
    a = len(results[0].boxes)
    for i in range(a):
        if results[0].boxes.id[i] == 1:
            keypoints_de_interes = results[0].keypoints[i].xyn.data.cpu().numpy()
            matriz_np = np.array(keypoints_de_interes)
            matriz_aplanada_np = matriz_np.flatten()
            valor = matriz_aplanada_np.tolist()
    # Retorna solo una lista plana
    return valor

def draw_landmark_on_image(results, frame):
    for result in results:
        # Check if the desired person ID is in the result
        for i, box in enumerate(result.boxes):
            if box.id == 1:  # If the box ID is 1
                keypoints = result.keypoints[i].xy.data.cpu().numpy()  # Get the keypoints for this box
                # Draw keypoints
                for kpt in keypoints:
                    for j, pt in enumerate(kpt):
                        x, y = int(pt[0]), int(pt[1])
                        # Check if the keypoint is part of the arm (shoulders, elbows, wrists)
                        if j in [5, 6, 7, 8, 9, 10]:
                            cv2.circle(frame, (x, y), radius=10, color=(0, 0, 255), thickness=-1)  # Red for arms
                        else:
                            cv2.circle(frame, (x, y), radius=9, color=(0, 255, 0), thickness=-1)  # Green for other keypoints
                    
                # Draw connections
                for conn in connections:
                    pt1 = keypoints[0][conn[0]]
                    pt2 = keypoints[0][conn[1]]
                    x1, y1 = int(pt1[0]), int(pt1[1])
                    x2, y2 = int(pt2[0]), int(pt2[1])
                    if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                        # Check if the connection is part of the arm
                        if conn == [5, 7] or conn== [7, 9] or conn==[6, 8] or conn==[8, 10]:
                            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 8)  # Red for arms
                        else:
                            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 7)  # verde for other connections
    return frame

def draw_landmark_on_result(results, frame):
    for result in results:
        # Check if the desired person ID is in the result
        for i, box in enumerate(result.boxes):
            if box.id == 1:  # If the box ID is 1
                keypoints = result.keypoints[i].xy.data.cpu().numpy()  # Get the keypoints for this box
                # Draw keypoints
                for kpt in keypoints:
                    for j, pt in enumerate(kpt):
                        x, y = int(pt[0]), int(pt[1])
                        # Check if the keypoint is part of the arm (shoulders, elbows, wrists)
                        if j in [5, 6, 7, 8, 9, 10]:
                            cv2.circle(frame, (x, y), radius=10, color=(255, 0, 0), thickness=-1)  # Red for arms
                        else:
                            cv2.circle(frame, (x, y), radius=6, color=(0, 255, 0), thickness=-1)  # Green for other keypoints
                    
                # Draw connections
                for conn in connections:
                    pt1 = keypoints[0][conn[0]]
                    pt2 = keypoints[0][conn[1]]
                    x1, y1 = int(pt1[0]), int(pt1[1])
                    x2, y2 = int(pt2[0]), int(pt2[1])
                    if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                        # Check if the connection is part of the arm
                        if conn == [5, 7] or conn== [7, 9] or conn==[6, 8] or conn==[8, 10]:
                            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 8)  # Red for arms
                        else:
                            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)  # verde for other connections
    return frame
def draw_class_on_image(label, img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    h, w, _ = img.shape
    # Ajustar el tamaño de la fuente basado en la altura y el ancho del video
    font_scale = min(h / 850, w / 850)
    y0, dy = int(30 * (h / 500)), int(15 * (h / 500))
    if label == "desplazamiento":
        message= "desplazamiento Correcto"
        fontColor = (0, 255, 0)  # Verde para desplazamiento
    elif label == "buen-golpe":
        message= "golpe Correcto"
        fontColor = (0, 255, 0)  # Verde para buen-golpe
    elif label == "manos":
        message = "Error:Durante el recorrido hacia la posicion de\nsalto y la batida inicial, el jugador muestra falta\nde coordinacion y fluidez, lo que afecta la\npreparacion adecuada para el remate.\nSolucion:Asegurate de que el movimiento de los\nbrazos y el balanceo sean consistentes, cuando\nestes finalizando el ultimo paso, tus manos\ntienen que ir ligeramente hacia\nabajo para mejorar el impulso del salto."
        fontColor = (255, 0, 0)  # Rojo para manos
    elif label == "mal-golpe":
        message = "Error:Durante el golpeo, el jugador muestra un\nbalanceo incorrecto del brazo, resultando\nen un contacto ineficaz con la pelota\ny una trayectoria de remate comprometida.\nSolucion:Manten el codo ligeramente flexionado\nal inicio del balanceo para generar potencia\ny extiendelo de manera controlada hacia\nadelante al golpear la pelota.Para que haci\ncuando remates el balon, lo pilles\nen tu maxima altura de tu salto y recuerda\n calcular tu salto con el balon de caida"
        fontColor = (255, 0, 0) # Rojo para mal-golpe
    else:
        message = ""
        fontColor = (255, 0, 0)  # Rojo intenso para errores no reconocidos
    thickness = max(int(min(h / 250, w / 250)), 1)
    lineType = 4
    # Dividir el mensaje en varias líneas
    lines = message.split('\n')
    # Calcular el tamaño del rectángulo de fondo
    text_widths = [cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines]
    max_text_width = max(text_widths)
    text_height = cv2.getTextSize(lines[0], font, font_scale, thickness)[0][1]
    padding = 8
    box_x0, box_y0 = int(10 * (w / 500)) - padding, y0 - text_height - padding
    box_x1, box_y1 = box_x0 + max_text_width + 2 * padding, box_y0 + len(lines) * dy + 2 * padding

    # Dibujar el rectángulo de fondo
    cv2.rectangle(img, (box_x0, box_y0), (box_x1, box_y1), (255, 255, 255), cv2.FILLED)
  
    # Dibujar cada línea del mensaje en la imagen
    for i, line in enumerate(lines):
        y = y0 + i * dy
        cv2.putText(img, line, (int(10 * (w / 500)), y), font, font_scale, fontColor, thickness, lineType)

    return img

def detect(model, lm_list):
    global label
    lm_list = np.array(lm_list)
    lm_list = np.expand_dims(lm_list, axis=0)
    result = model.predict(lm_list)
    if result[0][0]> 0.5:
        label = "desplazamiento"
    elif result[0][1] > 0.5:
        label = "buen-golpe"
    elif result[0][2] > 0.5:
        label = "manos"
    elif result[0][3] > 0.5:
        label = "mal-golpe"
    print(label)
    return label

@app.post("/video")
async def process_video(video: UploadFile = File(...)):
    allowed_file_types = ["video/mp4", "video/mpeg", "video/avi"]

    # Verificar el tipo de contenido del archivo recibido
    print(f"Received file content type: {video.content_type}")
    if video.content_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    yolo_detector = YOLO("C:\MI-CARRERA\Semestre7\SIS330\PROYECTO\yolov8n-pose.pt")
    try:
        # Guardar el archivo subido en el servidor
        video_path = "video_recibido2.mp4"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Procesar el video
        print("Video guardado correctamente.")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open video file")
        
        # Obtener tamaño del video para inicializar VideoWriter
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (frame_width, frame_height))

        global lm_list
        lm_list = []  # Reiniciar lista de landmarks
        label = ""  # Inicializar label
        i = 0
        warm_up_frames = 1

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("No se pudo leer el frame o fin del video.")
                break
            results = yolo_detector.track(frame, persist=True)
            i += 1
            print(i)

            if i % warm_up_frames == 0:
                if results[0]:
                    #print("si paso")
                    lm = make_landmark_timestep(results)
                    lm_list.append(lm)
                    if len(lm_list) == 20:
                        label = detect(model, lm_list)
                        lm_list.pop(0)
                        #lm_list=[]
                    if label=="manos" or label =="mal-golpe":
                        frame = draw_landmark_on_result(results, frame)
                    else:
                        frame = draw_landmark_on_image(results,frame)
                    frame = draw_class_on_image(label, frame)
                    #label =""
                out.write(frame)

        cap.release()
        out.release()

        print("Video procesado y guardado correctamente.")
        return FileResponse(output_path, media_type="video/mp4", filename="video.mp4")
    
    except Exception as e:
        print(f"Error procesando el video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process video: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
