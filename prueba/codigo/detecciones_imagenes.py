import os
import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('yolov8x-pose.pt')

# Directorio donde se encuentran las carpetas 'buenos' y 'malos'
directorio_principal = "C:\\MI-CARRERA\\Semestre 7\\SIS330\\PROYECTO\\Nueva carpeta\\imagenes\\Buenos\\3"
#carpeta_buenos = os.path.join(directorio_principal, "buenos")
resultados_carpeta_actual = []

for archivo in os.listdir(directorio_principal):
    ruta_archivo = os.path.join(directorio_principal, archivo)
        
    # Leer el fotograma del archivo
    frame = cv2.imread(ruta_archivo)

    # Run YOLOv8 tracking on the frame, persisting tracks between frames
    results = model.track(frame, persist=True)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Guardar el resultado en la carpeta 'buenos_resultados'
    carpeta_resultados = os.path.join(directorio_principal, "buenos_resultados")
    os.makedirs(carpeta_resultados, exist_ok=True)
    cv2.imwrite(os.path.join(carpeta_resultados, archivo), annotated_frame)

# Informar que la operación ha finalizado
print("Proceso completado.")
#print(results)