from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil

app = FastAPI()

@app.post("/video")
async def process_video(video: UploadFile = File(...)):
    # Lista de tipos de archivo permitidos
    allowed_file_types = ["video/mp4", "video/mpeg", "video/avi"]

    # Imprimir el tipo de contenido del archivo recibido
    print(f"Received file content type: {video.content_type}")

    # Verifica si el archivo es de un tipo válido
    if video.content_type not in allowed_file_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        # Guardar el archivo subido en el servidor
        with open("video.mp4", "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")
    
    # Devolver el archivo guardado al cliente
    return FileResponse("video.mp4", media_type="video/mp4", filename="video.mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
