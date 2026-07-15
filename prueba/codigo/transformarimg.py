import cv2
import albumentations as A
import numpy as np

# Definir la transformación de aumento de datos
transform = A.Compose([
    A.RandomBrightnessContrast(brightness_limit=(0.0,0.0), contrast_limit=(0.5,0.5), p=1),
    A.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1)  # Ajuste aleatorio de brillo y contraste
])

# Cargar una imagen
image_path = "C:\\MI-CARRERA\\Semestre7\\SIS330\\PROYECTO\\imagenes\\buenos\\11\\11_01_inicio..jpg"
image = cv2.imread(image_path)
# Aplica un filtro vintage (efecto sepia)
def aplicar_filtro_vintage(imagen):
    # Matriz de transformación para el efecto sepia
    matriz_sepia = np.array([[0.392, 0.534, 0.231],
                             [0.349, 0.586, 0.268],
                             [0.393, 0.569, 0.389]])

    # Aplica la transformación a la imagen
    imagen_sepia = cv2.transform(imagen, matriz_sepia)

    return imagen_sepia

# Aplica el filtro
imagen_vintage = aplicar_filtro_vintage(image)
# Aplicar la transformación
#transformed = transform(image=image)
#transformed_image = transformed["image"]
# Verifica la cantidad de canales
if imagen_vintage.shape[2] == 3:
    print("La imagen está en formato RGB.",imagen_vintage.shape)
else:
    print("La imagen no está en formato RGB.")

import matplotlib.pyplot as plt

plt.imshow(cv2.cvtColor(imagen_vintage, cv2.COLOR_BGR2RGB))
plt.title('modificada')
plt.axis('off')  # Oculta los ejes
plt.show()
