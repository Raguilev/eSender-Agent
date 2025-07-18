import threading
import datetime
from typing import Callable, Dict
from core.crypto_utils import descifrar_configuracion
from core.log_handler import registrar_log

class RPAScheduler:

    def __init__(self, manager_ref):
        self.manager = manager_ref
        self.tareas_programadas: Dict[str, Dict] = {}

    def _calcular_tiempo_inicial(self, hora_inicio: str) -> int:
        ahora = datetime.datetime.now()
        h, m = map(int, hora_inicio.split(":"))
        proximo = ahora.replace(hour=h, minute=m, second=0, microsecond=0)
        if proximo <= ahora:
            proximo += datetime.timedelta(days=1)
        return int((proximo - ahora).total_seconds())

    def _get_intervalo_segundos(self, frecuencia: str, intervalo: int) -> int:
        mapping = {
            "hourly": 3600,
            "daily": 86400,
            "weekly": 604800
        }
        if frecuencia not in mapping:
            raise ValueError(f"Frecuencia no válida: {frecuencia}")
        return intervalo * mapping[frecuencia]

    def programar_rpa(self, nombre: str, config: Dict, funcion_ejecucion: Callable):
        prog = config.get("programacion")
        if not prog:
            registrar_log(nombre, "[!] No se encontró configuración de programación.")
            return

        frecuencia = prog.get("frecuencia")
        intervalo = prog.get("intervalo")
        hora_inicio = prog.get("hora_inicio")

        if not (frecuencia and intervalo and hora_inicio):
            registrar_log(nombre, "[!] Configuración de programación incompleta.")
            return

        if nombre in self.tareas_programadas:
            registrar_log(nombre, "[i] Ya existe una programación activa.")
            return

        try:
            delay_inicial = self._calcular_tiempo_inicial(hora_inicio)
            intervalo_s = self._get_intervalo_segundos(frecuencia, int(intervalo))
        except Exception as e:
            registrar_log(nombre, f"[!] Error en configuración: {e}")
            return

        stop_event = threading.Event()

        def ejecutar_periodicamente():
            if stop_event.wait(timeout=delay_inicial):
                return  # Cancelado antes de comenzar
            while not stop_event.is_set():
                registrar_log(nombre, "RPA - Inicio de ejecución")
                try:
                    funcion_ejecucion(nombre)
                    registrar_log(nombre, "RPA - Ejecución finalizada")
                except Exception as e:
                    registrar_log(nombre, f"[ERROR] Fallo al ejecutar RPA: {e}")
                if stop_event.wait(timeout=intervalo_s):
                    break

        hilo = threading.Thread(target=ejecutar_periodicamente, daemon=True)
        hilo.start()
        self.tareas_programadas[nombre] = {"thread": hilo, "stop_event": stop_event}
        registrar_log(nombre, f"RPA - Programado cada {intervalo} {frecuencia} desde {hora_inicio}")

    def programar_si_corresponde(self, nombre: str, ruta_enc: str, ruta_key: str):
        try:
            config = descifrar_configuracion(ruta_enc, ruta_key)
            self.programar_rpa(nombre, config, self.manager.ejecutar_rpa)
        except Exception as e:
            registrar_log(nombre, f"[!] No se pudo programar: {e}")

    def cancelar(self, nombre: str):
        tarea = self.tareas_programadas.get(nombre)
        if tarea:
            tarea["stop_event"].set()
            registrar_log(nombre, "RPA - Programación cancelada.")
            del self.tareas_programadas[nombre]
        else:
            registrar_log(nombre, "[!] No se encontró tarea programada para cancelar.")