import flet as ft

def main(page: ft.Page):

    selected_path = None  # Variable para almacenar la ruta de la carpeta seleccionada
    path_text = ft.Text("Ruta seleccionada: ", selectable=True)  # Texto para mostrar la ruta seleccionada

    async def file_picker_result(e: ft.FilePickerResultEvent):
        nonlocal selected_path
        if e.path:  # e.path se usa para obtener la ruta seleccionada
            selected_path = e.path
            path_text.value = f"Ruta seleccionada: {selected_path}"  # Actualiza el texto con la ruta
            page.update()  # Actualiza la página para reflejar los cambios

    # Crear el FilePicker para seleccionar carpetas
    file_picker = ft.FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)

    select_btn = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        style=ft.ButtonStyle(
            padding=5,
            color="#ffffff",
            bgcolor="#393941",
            shape=ft.RoundedRectangleBorder(radius=5),
        ),
        on_click=lambda _: file_picker.get_directory_path()  # Cambiamos a get_directory_path para seleccionar una carpeta
    )

    contenido = ft.Column(
        controls=[
            path_text,  # Agrega el texto que muestra la ruta seleccionada
            select_btn
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(contenido)

ft.app(main, assets_dir="assets")
