import os
import time
from typing import List

DIRECTORIO_LOGS = os.path.join(os.getcwd(), "logs_rpa")
os.makedirs(DIRECTORIO_LOGS, exist_ok=True)

def _ruta_log(nombre_rpa: str) -> str:
    nombre_archivo = f"{nombre_rpa}.log"
    return os.path.join(DIRECTORIO_LOGS, nombre_archivo)

def registrar_log(nombre_rpa: str, mensaje: str):
    if not nombre_rpa or not nombre_rpa.strip():
        return

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    linea_log = f"[{timestamp}] {mensaje.strip()}\n"
    ruta = _ruta_log(nombre_rpa.strip())

    try:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(linea_log)
    except Exception as e:
        print(f"[ERROR] No se pudo registrar log para {nombre_rpa}: {e}")

def obtener_log_completo(nombre_rpa: str) -> List[str]:
    ruta = _ruta_log(nombre_rpa)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception:
        return [f"[ERROR] No se pudo leer el log de {nombre_rpa}."]

def obtener_resumen_logs(cantidad_lineas: int = 1) -> List[str]:
    resumen = []

    for archivo in os.listdir(DIRECTORIO_LOGS):
        if archivo.endswith(".log"):
            nombre_rpa = archivo[:-4]
            ruta = os.path.join(DIRECTORIO_LOGS, archivo)

            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    lineas = f.readlines()
                    if lineas:
                        ultimas = lineas[-cantidad_lineas:]
                        resumen.append(f"{nombre_rpa}: {ultimas[-1].strip()}")
                    else:
                        resumen.append(f"{nombre_rpa}: [Sin registros]")
            except Exception as e:
                resumen.append(f"{nombre_rpa}: [Error al leer log] {e}")

    return resumen

def borrar_log_rpa(nombre_rpa: str):
    ruta = _ruta_log(nombre_rpa)
    try:
        if os.path.exists(ruta):
            os.remove(ruta)
    except Exception as e:
        print(f"[ERROR] No se pudo borrar el log de {nombre_rpa}: {e}")

def borrar_todos_los_logs():
    for archivo in os.listdir(DIRECTORIO_LOGS):
        if archivo.endswith(".log"):
            try:
                os.remove(os.path.join(DIRECTORIO_LOGS, archivo))
            except Exception as e:
                print(f"[ERROR] No se pudo borrar {archivo}: {e}")

def obtener_total_logs_rpa() -> int:
    return len(listar_logs_disponibles())

def listar_logs_disponibles() -> List[str]:
    return [archivo[:-4] for archivo in os.listdir(DIRECTORIO_LOGS) if archivo.endswith(".log")]