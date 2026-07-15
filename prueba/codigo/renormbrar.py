import os
def renombrar_archivos(carpeta_imagenes, nombre):
    # Obtener la lista de archivos en la carpeta
    #print(carpeta_imagenes)
    archivos = os.listdir(carpeta_imagenes)
    #print(archivos)

    # Contador de fotogramas
    contador = 1
 
    # Crear subcarpeta
    ruta_subcarpeta = os.path.join(carpeta_imagenes,nombre+"-")
    os.makedirs(ruta_subcarpeta, exist_ok=True)
    print(ruta_subcarpeta)
    # Renombrar cada archivo
    for archivo in archivos:
        # Obtener el nombre del archivo sin la extensión
        nombre_archivo = os.path.splitext(archivo)[0]
        #print(nombre_archivo)
        # Renombrar el archivo
        nuevo_nombre = f"{carpeta_imagenes}_{contador:02d}"
        if contador == 1:
            nuevo_nombre += "_inicio"
        elif contador == len(archivos):
            nuevo_nombre += "_fin"

        nuevo_nombre += f".{os.path.splitext(archivo)[1]}"

        # Crear subcarpeta
        #ruta_subcarpeta = os.path.join(carpeta_imagenes,nombre+"--")
        #os.makedirs(ruta_subcarpeta, exist_ok=True)
        #print(ruta_subcarpeta)

        # Mover archivo renombrado
        os.rename(os.path.join(carpeta_imagenes, archivo), os.path.join(ruta_subcarpeta, nuevo_nombre))

        # Incrementar el contador
        contador += 1

# Ejemplo de uso
carpeta_principal = "C:\\MI-CARRERA\\Semestre7\\SIS330\\imagenes"
#C:\MI-CARRERA\Semestre7\SIS330\imagenes
# Obtener la lista de subcarpetas
subcarpetas = os.listdir(carpeta_principal)

# Renombrar los archivos en cada subcarpeta
for subcarpeta in subcarpetas:
    print(subcarpeta)
    ruta_subcarpeta = os.path.join(carpeta_principal, subcarpeta)
    print(ruta_subcarpeta)
    ruta_archivo_original = os.path.join(carpeta_principal, subcarpeta)
    renombrar_archivos(ruta_subcarpeta, subcarpeta)

print("Proceso completado.")
