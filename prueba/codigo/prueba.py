import os
import cv2
import albumentations as A
import numpy as np

# Definir la transformación de aumento de datos
transform = A.Compose([
    A.RandomBrightnessContrast(brightness_limit=(0.0, 0.0), contrast_limit=(0.5, 0.5), p=1),
    A.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1)  # Ajuste aleatorio de brillo y contraste
])

# Ruta de la carpeta principal que contiene subcarpetas con imágenes
carpeta_principal = "C:\\MI-CARRERA\\Semestre7\\SIS330\\PROYECTO\\fitro\\malos"
carpeta_destino = "C:\\MI-CARRERA\\Semestre7\\SIS330\\PROYECTO\\fitro\\malos"
# Aplica un filtro vintage (efecto sepia)
def aplicar_filtro_vintage(imagen):
    # Matriz de transformación para el efecto sepia
    matriz_sepia = np.array([[0.292, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])

    # Aplica la transformación a la imagen
    imagen_sepia = cv2.transform(imagen, matriz_sepia)

    return imagen_sepia
# Itera a través de las subcarpetas
for subcarpeta in os.listdir(carpeta_principal):
    subcarpeta_path = os.path.join(carpeta_principal, subcarpeta)
    #print(subcarpeta)
    if os.path.isdir(subcarpeta_path):
        for imagen_nombre in os.listdir(subcarpeta_path):
            #print(imagen_nombre)
            #ruta de la imagen
            imagen_path = os.path.join(subcarpeta_path, imagen_nombre)
            imagen = cv2.imread(imagen_path)

            # Aplica un filtro vintage (efecto sepia)
            imagen_vintage = aplicar_filtro_vintage(imagen)
            if imagen_vintage.shape[2] == 3:
                print("La imagen está en formato RGB.",imagen_vintage.shape)
                # Guarda la imagen resultante en otra carpeta  # Reemplaza con la ruta adecuada
                carpeta_resultados = os.path.join(carpeta_destino, subcarpeta+"FF")
                os.makedirs(carpeta_resultados, exist_ok=True)
                cv2.imwrite(os.path.join(carpeta_resultados, imagen_nombre), imagen_vintage)
            else:
                print("La imagen no está en formato RGB.")

            # Guarda la imagen resultante en otra carpeta  # Reemplaza con la ruta adecuada
            #carpeta_resultados = os.path.join(carpeta_destino, subcarpeta+"-")
            #os.makedirs(carpeta_resultados, exist_ok=True)
            #cv2.imwrite(os.path.join(carpeta_resultados, imagen_nombre), imagen_vintage)

            #print(f"Imagen procesada y guardada en {imagen_destino_path}")

print("Proceso completo")