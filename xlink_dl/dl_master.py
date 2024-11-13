"""
Módulo que se encarga de la descarga de archivos mediante una url
"""
import os
import random
import yarl
import requests
from mimetypes import guess_extension

MAX_RETRIES = 5  # Número máximo de reintentos
CHUNK_SIZE = 8192  # Tamaño del chunk para la descarga

def get_file_extension(url: str) -> str:
    """Obtiene la extensión del archivo usando el encabezado Content-Type con una solicitud HEAD."""
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "")
        extension = guess_extension(content_type.split(";")[0].strip())
        return extension if extension else ""
    except requests.RequestException as e:
        print(f"Error obteniendo el Content-Type: {e}")
        return ""

def get_name(url: str, response: requests.Response) -> str:
    """Obtiene el nombre del archivo desde la respuesta o genera uno con una extensión adecuada."""
    try:
        filename: str = response.headers["Content-Disposition"]
        filename = filename.split("filename=")[1].strip().replace('"', "")
    except KeyError:
        filename = yarl.URL(url).name.strip() or str(random.randint(1000000, 9999999999))

    if '.' not in filename.split('/')[-1]:
        extension = get_file_extension(url)
        if extension:
            filename += extension

    return filename

def get_size(response: requests.Response) -> int:
    """Obtiene el tamaño del archivo desde la cabecera de respuesta."""
    try:
        return int(response.headers.get("Content-Length", 0))
    except (TypeError, ValueError):
        return 0

def format_size(bytes_size: float) -> str:
    """Convierte el tamaño en bytes a un formato legible (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

def download_file(urls, ruta_dl, callback=None):
    """Descarga un archivo de la URL con reintentos y reanudación de descarga en caso de interrupción."""
    print(urls)
    retries = 0
    filename = None
    session = requests.Session()

    if not isinstance(urls, str):
        print(f"URL inválida: {urls}")
        return

    while retries < MAX_RETRIES:
        try:
            # Obtener el tamaño del archivo existente para reanudar
            file_path = os.path.join(ruta_dl, filename) if filename else None
            start_byte = os.path.getsize(file_path) if file_path and os.path.exists(file_path) else 0
            
            # Añadir encabezado 'Range' para solicitar descarga parcial
            headers = {'Range': f'bytes={start_byte}-'} if start_byte else {}

            # Realizar la solicitud
            with session.get(urls, headers=headers, stream=True) as response:
                response.raise_for_status()
                
                if not filename:
                    filename = get_name(urls, response)
                    file_path = os.path.join(ruta_dl, filename)
                
                size = get_size(response) + start_byte if start_byte else get_size(response)
                cbytes = start_byte

                # Guardar el archivo
                with open(file_path, "ab" if start_byte else "wb") as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):

                        cbytes += len(chunk)
                        f.write(chunk)
                        
                        # Progreso de descarga
                        percent = int(cbytes / size * 100) if size else 0
                        downloaded_size = format_size(cbytes)
                        total_size = format_size(size)

                        # Llamar al callback con los datos
                        if callback:
                            callback(filename, percent, downloaded_size, total_size)
                        print(f"{filename} - {percent}% ({downloaded_size}/{total_size})")
                    print(f"{filename} descargado.")
                return

        except requests.RequestException as e:
            print(f"Error en la descarga: {e}")
            retries += 1
            print(f"Reintentando descarga ({retries}/{MAX_RETRIES}) para {urls}...")
            continue

    print(f"Descarga fallida después de {MAX_RETRIES} intentos para {urls}")
