import flet as ft



# ------------------------------------
def create_setting_page(page):
    title = ft.Text("Ajustes", size=30)


    #Sección para que salga todo en la pagina de settings
    setting_page = ft.Stack(
        [
            ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
        ],
        width=681,
        height=478,
    )

    return setting_page