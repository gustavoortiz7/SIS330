import requests

# Ruta del archivo de video que deseas enviar
video_file_path = "C:\\EV\\PROYECTO\\prueba\\VideodeWhatsAp2024-05-27alas13.37.27_cfb6f1cc.mp4"

# URL del endpoint del servidor
url = "http://localhost:8000/process_video/"

# Leer el archivo de video
with open(video_file_path, 'rb') as video_file:
    # Leer los primeros bytes del archivo para ver cómo se están enviando
    first_bytes = video_file.read(100)
    print("Primeros 100 bytes del video en hexadecimal:", first_bytes.hex())

    # Reiniciar el puntero del archivo al inicio
    video_file.seek(0)
    
    files = {'file': video_file}
    response = requests.post(url, files=files)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Guardar el video procesado recibido
    with open("C:\\EV\\PROYECTO\\prueba\\output_processed.avi", 'wb') as output_file:
        output_file.write(response.content)
    print("Video procesado guardado con éxito.")
else:
    print("Error en la solicitud: ", response.status_code, response.text)
