import threading
import cv2
import mediapipe as mp
import numpy as np
import keras

cap = cv2.VideoCapture("C:\EV\PROYECTO\prueba\VideodeWhatsAp2024-05-27alas13.37.27_cfb6f1cc.mp4")
#cap = cv2.VideoCapture(0)
mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_path = "C:\\EV\\PROYECTO\\prueba\\output.mp4"
out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))


model = keras.models.load_model("C:\\EV\\PROYECTO\\lstm-model99.h5")

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
        cv2.circle(frame, (x1, y1), 3, (0, 255, 0), cv2.FILLED)
    
    for connection in connections:
        lm1 = results.pose_landmarks.landmark[connection[0]]
        lm2 = results.pose_landmarks.landmark[connection[1]]
        x1, y1 = int(lm1.x * w), int(lm1.y * h)
        x2, y2 = int(lm2.x * w), int(lm2.y * h)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
    return frame
def draw_class_on_image(label, img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 30)
    fontScale = 1
    if label == "buenosremates":
        fontColor = (0, 0, 255)
    else:
        fontColor = (0, 255, 0)
    thickness = 2
    lineType = 2
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
    if result[0][0] > 0.5:
        label = "buenosremates"
    else:
        label = "malosremates"
    return label

def process_batch(batch):
    global label
    result = detect(model, batch)
    label = result

def capture_and_process_frames():
    global lm_list
    i = 0
    warm_up_frames =1

    while True:
        ret, frame = cap.read()
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frameRGB)
        i += 1
        
        if i % warm_up_frames == 0:
            if results.pose_landmarks:
                lm = make_landmark_timestep(results)
                lm_list.append(lm)
                
                if len(lm_list) == 20:
                    # Procesar el lote de fotogramas
                    detect(model, lm_list,)
                    lm_list.pop(0)
                    #print(len(lm_list))

                frame = draw_landmark_on_image(mpDraw, results, frame)
            frame = draw_class_on_image(label, frame)
            out.write(frame)
            cv2.imshow("imagen", frame)
        
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_process_frames()
