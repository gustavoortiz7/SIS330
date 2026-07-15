import os

def unir_archivos_txt(files_path, output_path):
    # Variable para almacenar la cabecera única
    cabecera = None
    # Lista para almacenar el contenido total que cumple con la cabecera única
    contenido_total = []
    
    # Iterar sobre cada archivo en la ruta especificada
    for file_name in os.listdir(files_path):
        # Verificar si es un archivo de texto
        if file_name.endswith('.txt'):
            file_path = os.path.join(files_path, file_name)
            with open(file_path, 'r') as file:
                # Leer las líneas del archivo
                lines = file.readlines()
                # Obtener la cabecera del archivo actual
                cabecera_actual = lines[0]
                # Verificar si es la primera vez que se lee un archivo
                if cabecera is None:
                    cabecera = cabecera_actual
                else:
                    # Verificar si la cabecera es diferente a la cabecera del primer archivo
                    if cabecera_actual != cabecera:
                        print(f"Advertencia: La cabecera del archivo '{file_name}' es diferente.")
                        continue  # Saltar este archivo si la cabecera es diferente
                # Agregar el contenido del archivo a la lista si cumple con la cabecera única
                contenido_total.extend(lines[1:])
    
    # Escribir el contenido combinado en un nuevo archivo
    with open(output_path, 'w') as output_file:
        # Escribir la cabecera única
        output_file.write(cabecera)
        # Escribir el contenido combinado
        output_file.writelines(contenido_total)

# Ejemplo de uso
#C:\MI-CARRERA\Semestre7\SIS330\PROYECTO\SIS330\dataset
directorio_archivos = 'C:\\MI-CARRERA\\Semestre7\\SIS330\\PROYECTO\\fitro\\dataset\\malosgolpeos'
archivo_salida = 'C:\\MI-CARRERA\\Semestre7\\SIS330\\PROYECTO\\fitro\\dataset\\malosgolpeos\\mal-golpe.txt'

unir_archivos_txt(directorio_archivos, archivo_salida)
