from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import cv2
import numpy as np
import mediapipe as mp
import keras
import shutil
import os

app = FastAPI()

# Cargar el modelo y configurar MediaPipe
model = keras.models.load_model("C:\\EV\\proyIA\\lstm15-final3.h5")
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_path = "C:\\EV\\PROYECTO\\prueba\\video_procesado.mp4"

keypoint_mapping = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

lm_list = []

def make_landmark_timestep(results):
    c_lm = []
    for idx in keypoint_mapping:
        lm = results.pose_landmarks.landmark[idx]
        c_lm.append(lm.x)
        c_lm.append(lm.y)
    return c_lm

def draw_landmark_on_image(mpDraw, results, frame):
    connections = [
        [0, 2], [0, 5], [2, 7], [5, 8], 
        [11, 12], [11, 13], [12, 14], [13, 15], 
        [14, 16], [11, 23], [12, 24], [23, 24], 
        [23, 25], [24, 26], [25, 27], [26, 28]
    ]
    h, w, _ = frame.shape
    for idx in keypoint_mapping:
        lm = results.pose_landmarks.landmark[idx]
        x1, y1 = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (x1, y1), 7, (0, 255, 0), cv2.FILLED)
    
    for connection in connections:
        lm1 = results.pose_landmarks.landmark[connection[0]]
        lm2 = results.pose_landmarks.landmark[connection[1]]
        x1, y1 = int(lm1.x * w), int(lm1.y * h)
        x2, y2 = int(lm2.x * w), int(lm2.y * h)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 6)
    return frame


def draw_class_on_image(label, img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    h, w, _ = img.shape
    # Ajustar el tamaño de la fuente basado en la altura y el ancho del video
    font_scale = min(h / 850, w / 850)
    y0, dy = int(30 * (h / 500)), int(17 * (h / 500))
    #bottomLeftCornerOfText = (int(10 * (w / 500)), int(30 * (h / 500)))
    if label == "desplazamiento":
        message= "desplazamiento Correcto"
        #solution = "Correcto."
        fontColor = (0, 255, 0)  # Verde para desplazamiento
    elif label == "buen-golpe":
        message= "golpe Correcto"
        #olution = "Correcto."
        fontColor = (0, 255, 0)  # Verde para buen-golpe
    elif label == "manos":
        message = "Error:Movimiento de manos en el Recorrido(batida)\nSolucion:Mueve tus manos hacia atras,\ncuando estes finalizando el ultimo paso,\ntus manos tienen que ir ligeramente hacia\nabajo para mejorar el impulso del salto."
        #solution = "Solucion: Mueve tus manos hacia atrás,cuando estes finalizando el ultimo paso , tus manos tienen que ir ligeramente hacia abajo para mejorar el impulso al final del salto."
        fontColor = (255, 0, 0)  # Rojo para manos
    elif label == "mal-golpe":
        message = "Error:Golpe realizado incorrectamente\nSolucion:Ajusta tu postura de tus codos,tus\ncodos tienen que estar bien estirados hacia arriba,\npara que haci cuando remates el balon,\nlo pilles en tu maxima altura de tu salto\ny recuerda calcular tu salto con el balon de caida"
        #solution = "Solucion: Ajusta tu postura de tus codos, tus codos tienes que estar bien estirados hacia arriba, para que haci cuando remates el balon, lo pilles en tu maxima altura de tu salto y recuerda calcular tu salto con el balon de caida ."
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

    # Dibujar el mensaje de error y solución en la imagen
    #cv2.putText(img, message, (bottomLeftCornerOfText[0], bottomLeftCornerOfText[1] + 30), font, font_scale, fontColor, thickness, lineType)
    #cv2.putText(img, solution, (bottomLeftCornerOfText[0], bottomLeftCornerOfText[1] + 60), font, font_scale, fontColor, thickness, lineType)
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
    return label

@app.post("/video")
async def process_video(video: UploadFile = File(...)):
    allowed_file_types = ["video/mp4", "video/mpeg", "video/avi"]

    # Verificar el tipo de contenido del archivo recibido
    print(f"Received file content type: {video.content_type}")
    if video.content_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
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
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            i += 1

            if i % warm_up_frames == 0:
                if results.pose_landmarks:
                    lm = make_landmark_timestep(results)
                    lm_list.append(lm)
                    if len(lm_list) == 15:
                        label = detect(model, lm_list)
                        #lm_list.pop(0)
                        lm_list=[]
                    frame = draw_landmark_on_image(mp_draw, results, frame)
                    frame = draw_class_on_image(label, frame)
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
