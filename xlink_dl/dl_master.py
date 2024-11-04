"""
Módulo que se encarga de la descarga de archivos mediante una url
"""
import asyncio
import os
import random
import yarl
import requests
from aiohttp import ClientSession, ClientResponseError
from mimetypes import guess_extension


    
MAX_RETRIES = 5  # Número máximo de reintentos

def cursor_arriba(n=1):
    print(f'\33[{n}A', end='')

def get_file_extension(url: str) -> str:
    """Obtiene la extensión del archivo usando el encabezado Content-Type con una solicitud HEAD."""
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "")
        # Usamos guess_extension para obtener la extensión a partir del content-type
        extension = guess_extension(content_type.split(";")[0].strip())
        return extension if extension else ""
    except requests.RequestException as e:
        print(f"Error obteniendo el Content-Type: {e}")
        return ""

def get_name(url, resp) -> str:
    """Obtiene el nombre del archivo desde la respuesta o genera uno con una extensión adecuada."""
    try:
        filename: str = resp.headers["Content-Disposition"]
        filename = filename.split("filename=")[1].strip().replace('"', "")
    except KeyError:
        filename = yarl.URL(url).name.strip() or str(random.randint(1000000, 9999999999))

    # Si el nombre no tiene extensión, intentamos obtenerla con get_file_extension
    if '.' not in filename.split('/')[-1]:  # Última parte del nombre
        extension = get_file_extension(url)
        if extension:
            filename += extension

    return filename

def get_size(resp) -> int:
    """Obtiene el tamaño del archivo desde la cabecera de respuesta."""
    try:
        return int(resp.headers.get("Content-Length", 0))
    except (TypeError, ValueError):
        return 0

def format_size(bytes_size):
    """Convierte el tamaño en bytes a un formato legible (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

async def download_file(url: str, session: ClientSession, ruta_dl, progress_callback=None):

    """Descarga un archivo de la URL con reintentos y reanudación de descarga en caso de interrupción."""
    retries = 0
    filename = None

    # Asegurarnos de que la URL es una cadena
    if not isinstance(url, str):
        print(f"URL inválida: {url}")
        return

    while retries < MAX_RETRIES:
        try:
            # Obtener el tamaño del archivo existente para reanudar
            file_path = os.path.join(ruta_dl, filename) if filename else None
            start_byte = os.path.getsize(file_path) if file_path and os.path.exists(file_path) else 0
            
            # Añadir encabezado 'Range' para solicitar descarga parcial
            headers = {'Range': f'bytes={start_byte}-'} if start_byte else {}

            # Realizar la solicitud
            async with session.get(url, headers=headers) as resp:
                if resp.status in range(200, 300) or resp.status == 206:
                    # Obtener el nombre del archivo una sola vez
                    if not filename:
                        filename = get_name(url, resp)
                        file_path = os.path.join(ruta_dl, filename)
                    
                    size = get_size(resp) + start_byte if start_byte else get_size(resp)
                    cbytes = start_byte

                    # Guardar el archivo en modo "append" si es una reanudación
                    with open(file_path, "ab" if start_byte else "wb") as f:
                        async for chunk in resp.content.iter_any():
                            cbytes += len(chunk)
                            f.write(chunk)
                            # Progreso de descarga en porcentaje y tamaño descargado
                            percent = int(cbytes / size * 100) if size else 0
                            downloaded_size = format_size(cbytes)
                            total_size = format_size(size)

                            # Llamar al callback para actualizar el progreso
                            if progress_callback:
                                progress_callback(filename, percent, downloaded_size, total_size)

                            print(f"{filename} - {percent}% ({downloaded_size}/{total_size})           ")
                            cursor_arriba()
                        print(f"{filename} descargado.                                                 ")
                    return

                else:
                    print(f"Error en la descarga: código de estado {resp.status}")
        except ClientResponseError as e:
            print(f"Error en la respuesta del servidor: {e}")
        except Exception as e:
            print(f"Error durante la descarga: {e}")

        retries += 1
        print(f"Reintentando descarga ({retries}/{MAX_RETRIES}) para {url}...")

    print(f"Descarga fallida después de {MAX_RETRIES} intentos para {url}")

async def download_files(urls, progress_callback=None, ruta_dl=None):
    """Descarga múltiples archivos de forma concurrente, permitiendo nombres personalizados."""
    # Si `urls` es una cadena, la convertimos en una lista de un solo elemento
    if isinstance(urls, str):
        urls = [urls]

    async with ClientSession() as session:
        tasks = [download_file(url, session, ruta_dl, progress_callback=progress_callback) for url in urls]
        await asyncio.gather(*tasks)

