import requests
import os
from flask import Flask, request

UPLOAD_FOLDER = 'uploads/'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Plantilla HTML básica
html_template = '''
<!doctype html>
<title>Upload a Video</title>
<h1>Upload a Video</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=video>
  <input type=submit value=Upload>
</form>
'''

def upload_video(file_path, content_type):
    # Enviar el archivo al servidor FastAPI
    url = "http://localhost:8000/video"
    with open(file_path, 'rb') as video_file:
        files = {'video': (os.path.basename(file_path), video_file, content_type)}
        print("file",files)
        response = requests.post(url, files=files)
    return response

def save_received_file(response, received_file_path):
    with open(received_file_path, 'wb') as f:
        f.write(response.content)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['video']
        if file.filename == '':
            return 'No selected file'
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            print("mm",file_path)
            file.save(file_path)
            print(file)

            # Obtener el tipo de contenido del archivo
            content_type = file.content_type
            print(content_type)

            # Imprimir el tipo de contenido del archivo
            print(f"Content type of uploaded file: {content_type}")

            # Enviar archivo al servidor FastAPI
            response = upload_video(file_path, content_type)

            if response.status_code == 200:
                received_file_path = os.path.join(UPLOAD_FOLDER, 'received_video2.mp4')
                save_received_file(response, received_file_path)
                return 'File uploaded and received successfully'
            else:
                return f"Error: {response.status_code}\n{response.text}"

    return html_template

if __name__ == '__main__':
    app.run(debug=True, port=5000)
