import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
import base64
import io
import cv2 
import numpy as np
def sende_frame(frame):
    _,buffer = cv2.imencode('.jpg',frame)
    response_image = base64.b64encode(buffer).decode('utf-8')
    url ="http://localhost:5000/process_frame"
    data = {
        "image":response_image
    }
    response = requests.post(url,json=data)
    return response.json()

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error al abrir la cámara")
        return
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        response = sende_frame(frame)
        if 'image' in response:
            encoded_image = response['image']
            label= response['label']
            image_bytes = base64.b64decode(encoded_image)
            np_arr =np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            cv2.putText(frame,label,(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2, cv2.LINE_AA)
            #image = Image.open(io.BytesIO(image_bytes))
            #image = ImageTk.PhotoImage(image)
            #label_image.configure(image=image)
            #label_image.image = image
        else:
            print(f"Error: {response.get('error')}")
        cv2.imshow("imagen",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()