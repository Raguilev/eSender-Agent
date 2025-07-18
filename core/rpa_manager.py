import os
import json
import threading
from datetime import datetime
from typing import Dict, List

from core.rpa_executor import ejecutar_rpa
from core.log_handler import registrar_log
from core.scheduler import RPAScheduler

DIRECTORIO_RPAS = os.path.join(os.getcwd(), "rpas_cargados")
os.makedirs(DIRECTORIO_RPAS, exist_ok=True)

class RPAManager:
    def __init__(self):
        self.rpas: Dict[str, Dict] = {}
        self.scheduler = RPAScheduler(self)
        self._cargar_rpas()

    def _cargar_rpas(self):
        for nombre in os.listdir(DIRECTORIO_RPAS):
            ruta_rpa = os.path.join(DIRECTORIO_RPAS, nombre)
            if os.path.isdir(ruta_rpa):
                ruta_enc = os.path.join(ruta_rpa, "rpa_config.enc")
                ruta_key = os.path.join(ruta_rpa, "rpa.key")
                ruta_meta = os.path.join(ruta_rpa, "meta.json")

                if os.path.isfile(ruta_enc) and os.path.isfile(ruta_key):
                    meta = {
                        "activo": True,
                        "descripcion": "",
                        "creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ejecuciones": 0
                    }
                    if os.path.isfile(ruta_meta):
                        try:
                            with open(ruta_meta, "r", encoding="utf-8") as f:
                                meta.update(json.load(f))
                        except Exception as e:
                            registrar_log(nombre, f"[!] Error cargando meta.json: {e}")

                    self.rpas[nombre] = {
                        "enc": ruta_enc,
                        "key": ruta_key,
                        "meta": meta
                    }

                    if meta.get("activo"):
                        self.scheduler.programar_si_corresponde(nombre, ruta_enc, ruta_key)

    def _guardar_meta(self, nombre: str):
        if nombre in self.rpas:
            ruta = os.path.join(DIRECTORIO_RPAS, nombre, "meta.json")
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(self.rpas[nombre]["meta"], f, indent=2, ensure_ascii=False)
            except Exception as e:
                registrar_log(nombre, f"[ERROR] No se pudo guardar meta.json: {e}")

    def agregar_rpa(self, nombre: str, ruta_enc: str, ruta_key: str, descripcion: str = "") -> bool:
        nombre = nombre.strip().replace(" ", "_")
        if not nombre or nombre in self.rpas:
            return False

        destino = os.path.join(DIRECTORIO_RPAS, nombre)
        os.makedirs(destino, exist_ok=True)

        nueva_enc = os.path.join(destino, "rpa_config.enc")
        nueva_key = os.path.join(destino, "rpa.key")

        try:
            with open(ruta_enc, "rb") as f_in, open(nueva_enc, "wb") as f_out:
                f_out.write(f_in.read())
            with open(ruta_key, "rb") as f_in, open(nueva_key, "wb") as f_out:
                f_out.write(f_in.read())

            self.rpas[nombre] = {
                "enc": nueva_enc,
                "key": nueva_key,
                "meta": {
                    "activo": False,
                    "descripcion": descripcion,
                    "creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ejecuciones": 0
                }
            }
            self._guardar_meta(nombre)
            registrar_log(nombre, f"[OK] RPA agregado correctamente.")
            return True
        except Exception as e:
            registrar_log(nombre, f"[ERROR] Fallo al agregar RPA: {e}")
            return False

    def eliminar_rpa(self, nombre: str) -> bool:
        if nombre not in self.rpas:
            return False
        try:
            self.scheduler.cancelar(nombre)
            carpeta = os.path.dirname(self.rpas[nombre]["enc"])
            for archivo in os.listdir(carpeta):
                os.remove(os.path.join(carpeta, archivo))
            os.rmdir(carpeta)
            del self.rpas[nombre]
            registrar_log(nombre, "[INFO] RPA eliminado.")
            return True
        except Exception as e:
            registrar_log(nombre, f"[ERROR] Fallo al eliminar RPA: {e}")
            return False

    def renombrar_rpa(self, nombre_actual: str, nuevo_nombre: str) -> bool:
        nuevo_nombre = nuevo_nombre.strip().replace(" ", "_")
        if nombre_actual not in self.rpas or not nuevo_nombre or nuevo_nombre in self.rpas:
            return False

        carpeta_actual = os.path.join(DIRECTORIO_RPAS, nombre_actual)
        carpeta_nueva = os.path.join(DIRECTORIO_RPAS, nuevo_nombre)

        try:
            os.rename(carpeta_actual, carpeta_nueva)
            nueva_enc = os.path.join(carpeta_nueva, "rpa_config.enc")
            nueva_key = os.path.join(carpeta_nueva, "rpa.key")

            self.scheduler.cancelar(nombre_actual)
            if self.rpas[nombre_actual]["meta"].get("activo"):
                self.scheduler.programar_si_corresponde(nuevo_nombre, nueva_enc, nueva_key)

            self.rpas[nuevo_nombre] = {
                "enc": nueva_enc,
                "key": nueva_key,
                "meta": self.rpas[nombre_actual]["meta"]
            }
            del self.rpas[nombre_actual]
            self._guardar_meta(nuevo_nombre)
            registrar_log(nuevo_nombre, "[INFO] RPA renombrado correctamente.")
            return True
        except Exception as e:
            registrar_log(nombre_actual, f"[ERROR] Fallo al renombrar RPA: {e}")
            return False

    def obtener_lista_rpas(self) -> List[str]:
        return list(self.rpas.keys())

    def ejecutar_rpa(self, nombre: str):
        if nombre not in self.rpas:
            return

        def _ejecutar():
            registrar_log(nombre, "RPA - Inicio de ejecución")
            resultado = ejecutar_rpa(self.rpas[nombre]["enc"], self.rpas[nombre]["key"])
            registrar_log(nombre, resultado)
            self.rpas[nombre]["meta"]["ejecuciones"] += 1
            self._guardar_meta(nombre)
            registrar_log(nombre, "RPA - Ejecución finalizada")

        hilo = threading.Thread(target=_ejecutar, daemon=True)
        hilo.start()

    def activar_rpa(self, nombre: str):
        if nombre in self.rpas:
            self.rpas[nombre]["meta"]["activo"] = True
            self._guardar_meta(nombre)
            self.scheduler.programar_si_corresponde(nombre, self.rpas[nombre]["enc"], self.rpas[nombre]["key"])
            registrar_log(nombre, "[INFO] RPA activado.")

    def desactivar_rpa(self, nombre: str):
        if nombre in self.rpas:
            self.rpas[nombre]["meta"]["activo"] = False
            self._guardar_meta(nombre)
            self.scheduler.cancelar(nombre)
            registrar_log(nombre, "[INFO] RPA desactivado.")

    def obtener_rpa_info(self, nombre: str) -> Dict:
        return self.rpas.get(nombre, {}).get("meta", {})