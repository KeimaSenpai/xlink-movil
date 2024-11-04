import re
import flet as ft
import requests

from xlink_dl.dl_master import download_files

# Variable para almacenar la ruta de la carpeta seleccionada
selected_path = None  

async def file_picker_result(e: ft.FilePickerResultEvent):
    global selected_path
    if e.path:
        selected_path = e.path
        print("Carpeta seleccionada:", selected_path)

async def download(e=None, urls=None):
    global selected_path
    urls = urls or url_list.value

    # Verificar si la URL contiene "https://xlink.cu/"
    if re.search(r"^https://xlink\.cu/", urls):
        if isinstance(urls, str):
            urls = [urls]

        request_data = {
            "enlaces": urls,
            "inverso": True  
        }
        api_url = "https://xlink-py-api-r6m6.onrender.com/procesar"

        try:
            response = requests.post(api_url, json=request_data)
            api_response_data = response.json()
            urls_des = api_response_data["enlaces"]
            return await download_files(urls=urls_des, ruta_dl=selected_path, progress_callback=update_progress)

        except requests.exceptions.RequestException:
            print("Error al conectar con la API")
    else:
        return await download_files(urls=urls, ruta_dl=selected_path, progress_callback=update_progress)
    

card_dl = None

# Definir la estructura de la tarjeta de descarga
title_text = ft.Text("")
progress_bar = ft.ProgressBar(value=0)
size_text = ft.Text("")

# Callback para actualizar el progreso
def update_progress(filename, percent, downloaded_size, total_size):
    if not card_dl.visible:
        card_dl.visible = True
        card_dl.update()

    title_text.value = filename
    progress_bar.value = percent / 100
    size_text.value = f"{downloaded_size} / {total_size}"
    title_text.update()
    progress_bar.update()
    size_text.update()

# ----------------------------------------------------------
def create_home_page(page):
    global url_list, file_picker, card_dl

    # Crear el FilePicker para seleccionar carpetas
    file_picker = ft.FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)

    url_list = ft.TextField(
        label='URL', 
        height=42,
        text_size=15, 
        border_color='#393941', 
        border_radius=7,
        cursor_color='#393941',
        cursor_height=20,
        label_style=ft.TextStyle(
            color='#7c7c8d'
        ),
    )

    dl_btn = ft.ElevatedButton(
        "Download",
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#393941",
            overlay_color="#0C0C0C",
            shape=ft.RoundedRectangleBorder(radius=3),
            shadow_color="#000000",
            elevation=5,
        ),
        on_click=download
    )

    select_btn = ft.IconButton(
        icon=ft.icons.FOLDER_OPEN,
        style=ft.ButtonStyle(
            padding=5,
            color="#ffffff",
            bgcolor="#393941",
            shape=ft.RoundedRectangleBorder(radius=5),
        ),
        on_click=lambda _: file_picker.get_directory_path()
    )

    btns = ft.Row(
        controls=[dl_btn, select_btn],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    card_dl = ft.Card(
        visible=False, 
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.ARCHIVE),
                        title=title_text,
                        subtitle=progress_bar,
                    ),
                    ft.Row(
                        [size_text],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ]
            ),
            width=400,
            padding=10,
        )
    )
# ---------------------------------------------------
    home_page = ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[url_list, btns, card_dl],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
        ],
        alignment=ft.alignment.center,
        expand=True
    )

    return home_page
