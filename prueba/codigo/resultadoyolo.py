from cProfile import label
import cv2
from ultralytics import YOLO
import pandas as pd
import numpy as np
import keras
import threading

cap = cv2.VideoCapture("C:\EV\PROYECTO\prueba\VideodeWhatsAp2024-05-27alas13.37.27_cfb6f1cc.mp4")

yolo_detector = YOLO("C:\MI-CARRERA\Semestre7\SIS330\PROYECTO\yolov8n-pose.pt")
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_path = "C:\\EV\\PROYECTO\\prueba\\output5.mp4"
out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

model = keras.models.load_model("C:\\EV\\proyIA\\lstm15-final2.h5")
connections = [
    [0, 1], [0, 2], [1, 3], [2, 4], 
    [5, 6], [5, 7], [6, 8], [7, 9], 
    [8, 10], [5, 11], [6, 12], [11, 12], 
    [11, 13], [12, 14], [13, 15], [14, 16]
]
lm_list = []
label = ""
def make_landmark_timestep(results):
    #c_lm = []
    a = len(results[0].boxes)
    for i in range(a):
        if results[0].boxes.id[i] == 1:
            keypoints_de_interes = results[0].keypoints[i].xyn.data.cpu().numpy()
            matriz_np = np.array(keypoints_de_interes)
            matriz_aplanada_np = matriz_np.flatten()
            #print("matriz",matriz_aplanada_np)
            valor = matriz_aplanada_np.tolist()
            #print("las",valor)
            #c_lm.append(valor)
    # Retorna solo una lista plana
    return valor
def draw_landmark_on_image(results,frame):
    for result in results:
        # Check if the desired person ID is in the result
        for i, box in enumerate(result.boxes):
            if box.id == 1:  # If the box ID is 1
                keypoints = result.keypoints[i].xy.data.cpu().numpy()  # Get the keypoints for this box
                # Draw keypoints
                for kpt in keypoints:
                    for pt in kpt:
                        x, y = int(pt[0]), int(pt[1])
                        cv2.circle(frame, (x, y), radius=3, color=(0, 255, 0), thickness=-1)
                    
                    # Draw connections
                for conn in connections:
                    for k in keypoints:                           
                        pt1 = k[conn[0]]
                        pt2 = k[conn[1]]
                        x1, y1 = int(pt1[0]), int(pt1[1])
                        x2, y2 = int(pt2[0]), int(pt2[1])
                        if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                            cv2.line(frame, (x1, y1), (x2, y2), color=(255, 0, 0))
    return frame
def draw_class_on_image(label, img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 30)
    fontScale = 2
    if label == "desplazamiento" or label=="buen-golpe":
        fontColor = (0, 0, 255)
    else:
        fontColor = (0, 255, 0)
    thickness = 2
    lineType = 3
    cv2.putText(img, str(label),
                bottomLeftCornerOfText,
                font,
                fontScale,
                fontColor,
                thickness,
                lineType)
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

i = 0
warm_up_frames = 1

while True:
    ret, frame = cap.read()
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = yolo_detector.track(frame, persist=True)
    i += 1
    if i > warm_up_frames:
        if results[0]:
            lm = make_landmark_timestep(results)
            lm_list.append(lm)
            if len(lm_list) == 15:
                detect(model, lm_list,)
                lm_list.pop(0)
                #print(len(lm_list))
            frame = draw_landmark_on_image(results,frame)
        frame=draw_class_on_image(label,frame)
        out.write(frame)
        cv2.imshow("imagen", frame)
        if cv2.waitKey(1) == ord('q'):
            break

df = pd.DataFrame(lm_list)
df.to_csv(label + ".txt")
cap.release()
out.release()
cv2.destroyAllWindows()
