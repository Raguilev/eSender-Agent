import threading
import platform
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

icon_ref = None

def crear_icono_tray(app_window):

    def mostrar_ventana(icon=None, item=None):
        app_window.showNormal()
        app_window.activateWindow()

    def salir_aplicacion(icon=None, item=None):
        global icon_ref
        if icon_ref:
            icon_ref.stop()
        app_window.close()

    def crear_icono():
        global icon_ref
        imagen_icono = generar_icono()
        menu = Menu(
            MenuItem("Mostrar ventana", mostrar_ventana),
            MenuItem("Salir", salir_aplicacion)
        )
        icon_ref = Icon("eSenderAgent", imagen_icono, "eSender Agent", menu)
        icon_ref.run()

    sistema = platform.system()
    if sistema == "Darwin":
        crear_icono()
    else:
        threading.Thread(target=crear_icono, daemon=True).start()

def generar_icono(size=64, color_bg="white", color_circle="black"):
    image = Image.new("RGB", (size, size), color_bg)
    draw = ImageDraw.Draw(image)
    margin = int(size * 0.15)
    draw.ellipse((margin, margin, size - margin, size - margin), fill=color_circle)
    return image