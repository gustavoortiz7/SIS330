from flask import Flask, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import keras
import base64
import os
import uuid

app = Flask(__name__)

# Cargar el modelo
model_path = "C:\\EV\\PROYECTO\\lstm-model99.h5"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")
model = keras.models.load_model(model_path)

# Configuración de Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Variables globales
keypoint_mapping = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
lm_list = []
label = ""

def make_landmark_timestep(results):
    c_lm = []
    for idx in keypoint_mapping:
        lm = results.pose_landmarks.landmark[idx]
        c_lm.append(lm.x)
        c_lm.append(lm.y)
    return c_lm

def draw_landmark_on_image(mp_draw, results, frame):
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
        cv2.circle(frame, (x1, y1), 3, (0, 255, 0), cv2.FILLED)
    
    for connection in connections:
        lm1 = results.pose_landmarks.landmark[connection[0]]
        lm2 = results.pose_landmarks.landmark[connection[1]]
        x1, y1 = int(lm1.x * w), int(lm1.y * h)
        x2, y2 = int(lm2.x * w), int(lm2.y * h)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
    return frame

def draw_class_on_image(label, img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 30)
    fontScale = 1
    fontColor = (0, 0, 255) if label == "buenosremates" else (0, 255, 0)
    thickness = 2
    lineType = 2
    cv2.putText(img, str(label), bottomLeftCornerOfText, font, fontScale, fontColor, thickness, lineType)
    return img

def detect(model, lm_list):
    global label
    lm_list = np.array(lm_list)
    lm_list = np.expand_dims(lm_list, axis=0)
    result = model.predict(lm_list)
    if result[0][0] > 0.5:
        label = "buenosremates"
    else:
        label = "malosremates"
    return str(label)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global lm_list, label
    try:
        data = request.json
        image_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frameRGB)

        if results.pose_landmarks:
            lm = make_landmark_timestep(results)
            lm_list.append(lm)
            if len(lm_list) == 20:
                detect(model, lm_list)
                lm_list.pop(0)

            frame = draw_landmark_on_image(mp_draw, results, frame)
        frame = draw_class_on_image(label, frame)

        _, buffer = cv2.imencode('.jpg', frame)
        response_image = base64.b64encode(buffer).decode('utf-8')
        response = {
            'label': label,
            'image': response_image
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
