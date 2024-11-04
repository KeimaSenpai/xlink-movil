import flet as ft

from views.home import create_home_page
from views.setting import create_setting_page

def main(page: ft.Page):
    page.window.width = 390
    page.window.height = 600

    info_text = ''' 
XLink creado por KeimaSenpai. El cual permite la descarga de archivos mediante xlink y enlaces estandars. 
'''

    dlg = ft.AlertDialog(
        title=ft.Text("XLink 1.0.0", size=15),
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Text(info_text, size=12),
                ft.Row(
                    spacing=4,
                    controls=[
                        ft.IconButton(
                            ft.icons.SEND,
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
        adaptive=True
    )


    async def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(
                        leading_width=30,
                        adaptive=True,
                        title=ft.Text("XLink", weight=ft.FontWeight.BOLD),
                        center_title=False,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        actions=[
                            ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(text="Ajustes", on_click=lambda _: page.go("/setting")),
                                    ft.PopupMenuItem(text=""),
                                    ft.PopupMenuItem(text="Info", on_click=lambda e: page.open(dlg)),
                                ],
                                shape=ft.RoundedRectangleBorder(radius=5),
                                icon_color='#ffffff'
                            ),
                        ]
                    ),


                    ft.Column(
                        # spacing=0,
                        controls=[
                            create_home_page(page),
                        ],
                        # alignment=ft.MainAxisAlignment.CENTER,
                    ),

                    ft.FloatingActionButton(
                        icon=ft.icons.ADD,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        elevation=30,
                        shape=ft.RoundedRectangleBorder(radius=50),
                        # on_click= 
                    ),

                ],
                # padding=0,
            )
        )

        if page.route == "/setting":
            page.views.append(
                ft.View(
                    "/setting",
                    [
                        ft.AppBar(
                            leading_width=30,
                            adaptive=True,
                            title=ft.Text("Ajustes", weight=ft.FontWeight.BOLD),
                            center_title=False,
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            actions=[]
                        ),
                        ft.Column(
                            # spacing=0,
                            controls=[
                                create_setting_page(page),
                            ],
                            # alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    # padding=0,
                )
            )
        page.update()

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        await page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)



ft.app(target=main, assets_dir="assets")

