import re
import flet as ft
import requests

from xlink_dl.dl_master import download_file


def main(page: ft.Page):
    page.title = "ChunkDL"
    page.window.width = 390
    page.window.height = 600


    class State:
        def __init__(self):
            self.selected_path = None
            
    state = State()

    async def file_picker_result(e: ft.FilePickerResultEvent):
        if e.path:
            state.selected_path = e.path
            print("Carpeta seleccionada:", state.selected_path)




    # Crear el FilePicker para seleccionar carpetas
    file_picker = ft.FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)

    url_list = ft.TextField(
        label='URL', 
        height=44,
        text_size=16, 
        border_color='#393941', 
        border_radius=7,
        cursor_color='#393941',
        cursor_height=20,
        label_style=ft.TextStyle(
            color='#7c7c8d'
        ),
    )

    progress_text = ft.Text("")  # Texto para mostrar el progreso

    def actualizar_progreso(filename, percent, downloaded_size, total_size):
        """Callback para actualizar el progreso en la interfaz."""
        progress_text.value = f"{filename} - {percent}% ({downloaded_size}/{total_size})"
        page.update()

    def download(e, urls=None):
        if not state.selected_path:
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor, seleccione una carpeta de destino"))
            )
            return

        if not urls and not url_list.value:
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor, ingrese una URL"))
            )
            return
        
        urls = urls or url_list.value

        # Si `urls` es una sola URL en forma de cadena, convertimos a lista para unificar el tratamiento
        if isinstance(urls, str):
            urls = [urls]

        # Verificar si la URL contiene "https://xlink.cu/"
        if all(re.search(r"^https://xlink\.cu/", url) for url in urls):
            request_data = {
                "enlaces": urls,
                "inverso": True
            }
            api_url = "https://xlink-py-api-r6m6.onrender.com/procesar"

            try:
                response = requests.post(api_url, json=request_data)
                api_response_data = response.json()
                urls_des = api_response_data["enlaces"]
                
                # Si `urls_des` es una lista, iteramos; si es una cadena, lo enviamos directamente
                if isinstance(urls_des, list):
                    for url in urls_des:
                        download_file(urls=urls_des, ruta_dl=state.selected_path, callback=actualizar_progreso)
                else:
                    download_file(urls=urls_des, ruta_dl=state.selected_path, callback=actualizar_progreso)

            except requests.exceptions.RequestException as e:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Error al conectar con la API: {str(e)}"))
                )
            except Exception as e:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Error durante la descarga: {str(e)}"))
                )
        else:
            # Caso en el que la URL no contiene "https://xlink.cu/"
            for url in urls:
                download_file(urls=url, ruta_dl=state.selected_path, callback=actualizar_progreso)


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
        on_click=download  # Llamamos a la función iniciar_descarga al hacer clic
    )

    select_btn = ft.IconButton(
        icon=ft.icons.FOLDER_OPEN,
        style=ft.ButtonStyle(
            padding=5,
            color="#ffffff",
            bgcolor="#393941",
            shape=ft.RoundedRectangleBorder(radius=5),
        ),
        on_click=lambda _: file_picker.get_directory_path()  # Cambiamos a get_directory_path para seleccionar una carpeta
    )

    btns = ft.Row(
        controls=[dl_btn, select_btn],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    info_text = ''' 
XLink creado por KeimaSenpai. El cual permite la descarga de archivos mediante xlink y enlaces estándar. 
'''

    dlg = ft.AlertDialog(
        title=ft.Text("XLink 1.0.0", size=15),
        content=ft.Column(
            spacing=5,
            height=120,
            controls=[
                ft.Text(info_text, size=12),
                ft.Row(
                    spacing=4,
                    controls=[
                        ft.IconButton(
                            ft.icons.LINK_ROUNDED,
                            style=ft.ButtonStyle(
                                color="#5B0098",
                                bgcolor="#0C0C0C",
                                shape=ft.RoundedRectangleBorder(radius=5),
                            ),
                            on_click=lambda _: page.launch_url("https://t.me/+uMnCUP8to8owMjFh"),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        adaptive=True,
        shape=ft.RoundedRectangleBorder(radius=5),
    )

    page.appbar = ft.AppBar(
        leading_width=30,
        title=ft.Text("XLink", weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Ajustes"),
                    ft.PopupMenuItem(text=""),
                    ft.PopupMenuItem(text="Info", on_click=lambda e: page.open(dlg)),
                ],
                shape=ft.RoundedRectangleBorder(radius=5),
            ),
        ]
    )

    # Agregar elementos a la interfaz
    page.add(
        ft.Column(
            controls=[
                ft.Text('Coloca el enlace aquí'),
                url_list,
                btns,
                progress_text,  # Agregar el texto de progreso a la interfaz
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main, assets_dir="assets")
