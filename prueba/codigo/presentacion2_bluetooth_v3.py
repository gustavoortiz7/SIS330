# Importamos las librerias
from ultralytics import YOLO
import cv2
import bluetooth
import pyttsx3
import time

# Inicializamos el motor de texto a voz
engine = pyttsx3.init()

# Leer nuestro modelo
model = YOLO("modelos/best_4_20E.pt")

# Dirección MAC de tu módulo Bluetooth
bd_addr = "00:23:07:35:f2:6b"  # Reemplaza con la dirección MAC de tu módulo Bluetooth
port = 1

# Conectar al dispositivo Bluetooth
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
try:
    sock.connect((bd_addr, port))
    print("Conectado a Bluetooth")
except bluetooth.btcommon.BluetoothError as err:
    print(f"Error al conectar a Bluetooth: {err}")
    exit()

# Realizamos la VideoCaptura
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Mapeo de números de clase a nombres
nombres_clases = {
    0: "cama",
    1: "gradas",
    2: "mesa",
    3: "puerta"
}

# Variables de control para mejorar el rendimiento
frame_count = 0
process_frame_interval = 5  # Procesar cada 5 fotogramas

# Hacemos un bucle
try:
    while True:
        # Leer fotogramas
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar el video")
            break

        # Procesar cada n-ésimo fotograma para reducir la carga
        if frame_count % process_frame_interval == 0:
            # Leer resultados de la detección
            resultados = model.predict(frame, imgsz=640)
            resultados = resultados[0]

            # Leer la distancia desde Arduino vía Bluetooth
            try:
                data = sock.recv(1024)
                distancia = float(data.decode().strip())
            except Exception as e:
                print(f"Error al leer desde Bluetooth: {e}")
                continue

            # Verificar si se detectó algún objeto
            if len(resultados.boxes) > 0:
                # Obtener la clase del primer objeto detectado
                objeto = resultados.boxes.cls.cpu().numpy()

                # Obtener el nombre de la clase
                clase = int(objeto[0])
                nombre_clase = nombres_clases.get(clase, "Desconocido")

                # Mostrar la distancia
                cv2.putText(frame, f"Distancia: {distancia} cm", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Decir el objeto detectado y la distancia
                engine.say(f"{nombre_clase} detectada, Distancia: {distancia} centímetros")
                engine.runAndWait()

        frame_count += 1

        # Mostrar resultados de la detección
        anotaciones = resultados.plot()

        # Mostrar nuestros fotogramas
        cv2.imshow("Deteccion", anotaciones)

        # Cerrar nuestro programa
        if cv2.waitKey(1) == 27:
            break

except KeyboardInterrupt:
    print("Interrupción del usuario")

finally:
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    sock.close()
    engine.stop()
