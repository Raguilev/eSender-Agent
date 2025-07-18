import os
import json
import traceback
from datetime import datetime
from core.log_handler import registrar_log
from core.crypto_utils import descifrar_configuracion
from core.mail_sender import enviar_reporte_por_correo
from core.navigator import ejecutar_navegacion


def ejecutar_rpa(ruta_enc: str, ruta_key: str) -> str:
    try:
        config = descifrar_configuracion(ruta_enc, ruta_key)
        if not config:
            return "[ERROR] Configuración descifrada vacía."

        nombre_rpa = config.get("rpa", {}).get("nombre", "RPA")
        registrar_log(nombre_rpa, "RPA: Inicio de ejecución")

        registrar_log(nombre_rpa, "RPA: Iniciando navegación y captura de URLs")
        capturas, detalles = ejecutar_navegacion(config)

        for detalle in detalles:
            registrar_log(nombre_rpa, f"RPA: URL accedida → {detalle.get('url')}")
            registrar_log(nombre_rpa, f"RPA: Tiempo de carga → {detalle.get('tiempo_carga', '?')}s")
            registrar_log(nombre_rpa, f"RPA: Captura realizada → {detalle.get('nombre_captura', 'No capturada')}")

        registrar_log(nombre_rpa, f"RPA: Total de capturas realizadas → {len(capturas)}")

        registrar_log(nombre_rpa, "RPA: Enviando correo...")
        enviar_reporte_por_correo(
            config.get("correo", {}),
            config.get("rpa", {}),
            capturas,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        registrar_log(nombre_rpa, "RPA: Envío de correo completado")

        registrar_log(nombre_rpa, "RPA: Ejecución finalizada")
        _incrementar_contador_ejecuciones(ruta_enc)

        return "[SUCCESS] RPA ejecutado con éxito."

    except Exception as e:
        error_msg = f"RPA: Error durante ejecución → {str(e)}\n{traceback.format_exc()}"
        registrar_log(nombre_rpa if 'nombre_rpa' in locals() else "rpa_desconocido", error_msg)
        return error_msg


def _incrementar_contador_ejecuciones(ruta_enc: str):
    carpeta_rpa = os.path.dirname(ruta_enc)
    ruta_meta = os.path.join(carpeta_rpa, "meta.json")
    datos = {}

    if os.path.exists(ruta_meta):
        try:
            with open(ruta_meta, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except Exception:
            datos = {}

    datos["ejecuciones"] = datos.get("ejecuciones", 0) + 1
    datos["ultima_ejecucion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(ruta_meta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARN] No se pudo actualizar meta.json: {e}")