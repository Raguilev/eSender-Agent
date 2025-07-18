import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout,
    QListWidget, QMessageBox, QInputDialog, QTextEdit, QCheckBox
)
from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtCore import QTimer, Qt
from core.rpa_manager import RPAManager
from core.log_handler import obtener_log_completo
from core.crypto_utils import descifrar_configuracion

class VentanaAgente(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eSender Agent")
        self.setGeometry(100, 100, 800, 550)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.tab_rpa = QWidget()
        self.tab_logs = QWidget()

        self.tab_widget.addTab(self.tab_rpa, "Carga de RPAs")
        self.tab_widget.addTab(self.tab_logs, "Resumen de Logs")

        self.rpa_manager = RPAManager()
        self.lineas_mostradas = set()
        self.inicializar_tab_rpa()
        self.inicializar_tab_logs()

        self.timer_logs = QTimer(self)
        self.timer_logs.timeout.connect(self.actualizar_logs)
        self.timer_logs.start(5000)

    def inicializar_tab_rpa(self):
        layout = QVBoxLayout()

        self.lista_rpas = QListWidget()
        layout.addWidget(QLabel("RPAs cargados:"))
        layout.addWidget(self.lista_rpas)

        self.lbl_rpa_estado = QLabel("Total RPAs activos: 0")
        layout.addWidget(self.lbl_rpa_estado)

        self.actualizar_lista_rpas()
        self.lista_rpas.currentItemChanged.connect(self.on_rpa_seleccionado)

        botones = QHBoxLayout()
        btn_cargar = QPushButton("Cargar nuevo RPA")
        btn_eliminar = QPushButton("Eliminar seleccionado")
        btn_renombrar = QPushButton("Renombrar seleccionado")
        btn_ejecutar = QPushButton("▶ Ejecutar ahora")
        btn_toggle = QPushButton("Activar/Inactivar")

        btn_cargar.clicked.connect(self.cargar_rpa)
        btn_eliminar.clicked.connect(self.eliminar_rpa)
        btn_renombrar.clicked.connect(self.renombrar_rpa)
        btn_ejecutar.clicked.connect(self.forzar_ejecucion)
        btn_toggle.clicked.connect(self.activar_inactivar)

        botones.addWidget(btn_cargar)
        botones.addWidget(btn_eliminar)
        botones.addWidget(btn_renombrar)
        botones.addWidget(btn_ejecutar)
        botones.addWidget(btn_toggle)

        layout.addLayout(botones)

        self.lbl_info = QLabel("Info de programación:")
        self.lbl_info.setWordWrap(True)
        layout.addWidget(self.lbl_info)

        self.tab_rpa.setLayout(layout)

    def inicializar_tab_logs(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Resumen de Ejecuciones:"))

        self.text_logs = QTextEdit()
        self.text_logs.setReadOnly(True)
        layout.addWidget(self.text_logs)

        btn_limpiar_vista = QPushButton("🧹 Limpiar pantalla")
        btn_limpiar_vista.clicked.connect(self.limpiar_logs_visuales)
        layout.addWidget(btn_limpiar_vista)

        self.tab_logs.setLayout(layout)

    def actualizar_lista_rpas(self):
        self.lista_rpas.clear()
        activos = 0
        for nombre in self.rpa_manager.obtener_lista_rpas():
            info = self.rpa_manager.obtener_rpa_info(nombre)
            item_str = f"🟢 {nombre}" if info.get("activo") else f"🔴 {nombre}"
            self.lista_rpas.addItem(item_str)
            if info.get("activo"):
                activos += 1
        self.lbl_rpa_estado.setText(f"Total RPAs activos: {activos}")

    def cargar_rpa(self):
        nombre, ok = QInputDialog.getText(self, "Nombre del RPA", "Asigna un nombre para este RPA:")
        if not ok or not nombre.strip():
            return

        descripcion, _ = QInputDialog.getText(self, "Descripción opcional", "Describe brevemente este RPA (opcional):")

        enc_path, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo .enc", filter="*.enc")
        if not enc_path:
            return

        key_path, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo .key", filter="*.key")
        if not key_path:
            return

        exito = self.rpa_manager.agregar_rpa(nombre.strip(), enc_path, key_path, descripcion.strip())
        if exito:
            QMessageBox.information(self, "Éxito", f"RPA '{nombre}' cargado exitosamente.")
            self.actualizar_lista_rpas()
        else:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el RPA '{nombre}'.")

    def eliminar_rpa(self):
        seleccionado = self.lista_rpas.currentItem()
        if seleccionado:
            nombre = seleccionado.text()[2:].strip()
            confirmar = QMessageBox.question(
                self, "Confirmar", f"¿Eliminar RPA '{nombre}'?", QMessageBox.Yes | QMessageBox.No
            )
            if confirmar == QMessageBox.Yes:
                self.rpa_manager.eliminar_rpa(nombre)
                self.actualizar_lista_rpas()

    def renombrar_rpa(self):
        seleccionado = self.lista_rpas.currentItem()
        if seleccionado:
            nombre_antiguo = seleccionado.text()[2:].strip()
            nombre_nuevo, ok = QInputDialog.getText(self, "Renombrar", f"Nuevo nombre para '{nombre_antiguo}':")
            if ok and nombre_nuevo.strip():
                try:
                    self.rpa_manager.renombrar_rpa(nombre_antiguo, nombre_nuevo.strip())
                    self.actualizar_lista_rpas()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def activar_inactivar(self):
        item = self.lista_rpas.currentItem()
        if item:
            nombre = item.text()[2:].strip()
            info = self.rpa_manager.obtener_rpa_info(nombre)
            if info.get("activo"):
                self.rpa_manager.desactivar_rpa(nombre)
            else:
                self.rpa_manager.activar_rpa(nombre)
            self.actualizar_lista_rpas()

    def actualizar_logs(self):
        entradas_nuevas = []
        nombres_logs = list(self.rpa_manager.rpas.keys())
        for nombre_rpa in nombres_logs:
            lineas = obtener_log_completo(nombre_rpa)
            for linea in lineas:
                entry = f"{nombre_rpa}: {linea.strip()}"
                if entry not in self.lineas_mostradas:
                    self.lineas_mostradas.add(entry)
                    entradas_nuevas.append(entry)

        if entradas_nuevas:
            self.text_logs.append("\n".join(entradas_nuevas))
            self.text_logs.append("-" * 80)

    def limpiar_logs_visuales(self):
        self.text_logs.clear()
        self.lineas_mostradas.clear()

    def forzar_ejecucion(self):
        item = self.lista_rpas.currentItem()
        if item:
            nombre = item.text()[2:].strip()
            self.rpa_manager.ejecutar_rpa(nombre)
            QMessageBox.information(self, "Ejecución", f"RPA '{nombre}' ejecutado manualmente.")

    def on_rpa_seleccionado(self):
        item = self.lista_rpas.currentItem()
        if not item:
            self.lbl_info.setText("Sin selección.")
            return

        nombre = item.text()[2:].strip()
        if nombre not in self.rpa_manager.rpas:
            self.lbl_info.setText("Sin información.")
            return

        try:
            info = self.rpa_manager.obtener_rpa_info(nombre)
            ruta_enc = self.rpa_manager.rpas[nombre]["enc"]
            ruta_key = self.rpa_manager.rpas[nombre]["key"]
            config = descifrar_configuracion(ruta_enc, ruta_key)
            prog = config.get("programacion", {})
            desc = info.get("descripcion", "")
            fecha = info.get("creacion", "Desconocido")
            ejecs = info.get("ejecuciones", 0)
            estado = "Activo" if info.get("activo") else "Inactivo"

            texto = f"Descripción: {desc}\nCreado: {fecha}\nEjecuciones: {ejecs}\nEstado: {estado}"
            if prog:
                texto += f"\nFrecuencia: {prog.get('frecuencia')} | Intervalo: {prog.get('intervalo')} | Inicio: {prog.get('hora_inicio')}"
            else:
                texto += "\nEste RPA no tiene configuración de programación."
            self.lbl_info.setText(texto)
        except Exception as e:
            self.lbl_info.setText(f"Error al leer configuración: {e}")

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()
