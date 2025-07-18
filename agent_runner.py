# agent_runner.py

import sys
import platform
from PyQt5.QtWidgets import QApplication
from ui.agent_window import VentanaAgente
from ui.tray_icon import crear_icono_tray

def main():
    app = QApplication(sys.argv)

    if platform.system() == "Darwin":
        try:
            from ctypes import cdll
            appkit = cdll.LoadLibrary('/System/Library/Frameworks/AppKit.framework/AppKit')
            appkit.NSApplication.sharedApplication().setActivationPolicy_(1)
        except Exception as e:
            print(f"Error al ocultar ícono del Dock: {e}")

    ventana = VentanaAgente()
    ventana.show()

    crear_icono_tray(ventana)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()