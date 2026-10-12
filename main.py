import flet as ft

from views.window import App

def main(page: ft.Page):
    App(page).view()

ft.run(main)
