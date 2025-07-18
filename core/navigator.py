import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from core.log_handler import registrar_log

def ejecutar_navegacion(rpa_config, screenshot_dir="Reportes"):
    rpa_data = rpa_config.get("rpa", {})
    url_rutas = rpa_data.get("url_ruta", [])
    nombre_rpa = rpa_data.get("nombre", "RPA")

    if not url_rutas:
        raise ValueError("No se encontraron rutas de navegación.")

    os.makedirs(screenshot_dir, exist_ok=True)
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    safe_timestamp = now.strftime("%Y-%m-%d_%H-%M-%S") if rpa_data.get("modo_navegador_visible", False) else "headless"

    capturas = []
    detalles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not rpa_data.get("modo_navegador_visible", False),
            args=["--ignore-certificate-errors"]
        )

        for idx, ruta in enumerate(url_rutas):
            url_actual = ruta.get("url")
            wait_time = int(ruta.get("wait_time_ms", 0))
            capturar = ruta.get("capturar", False)
            requiere_auth = ruta.get("requiere_autenticacion", False)
            tipo_auth = ruta.get("tipo_autenticacion", "")

            if not url_actual:
                raise ValueError(f"URL vacía en la posición {idx + 1}")

            context_args = {
                "viewport": {
                    "width": rpa_data.get("pantalla", {}).get("viewport_width", 1920),
                    "height": rpa_data.get("pantalla", {}).get("viewport_height", 1080)
                },
                "ignore_https_errors": True
            }

            if requiere_auth and tipo_auth == "http_basic":
                creds = ruta.get("http_basic", {})
                context_args["http_credentials"] = {
                    "username": creds.get("username", ""),
                    "password": creds.get("password", "")
                }

            with browser.new_context(**context_args) as context:
                page = context.new_page()
                registrar_log(nombre_rpa, f"[{idx + 1}] Navegando a: {url_actual}")

                tiempo_inicio = time.time()
                page.goto(url_actual, timeout=60000)
                tiempo_fin = time.time()
                tiempo_carga = round(tiempo_fin - tiempo_inicio, 2)

                if requiere_auth and tipo_auth == "form_js":
                    form = ruta.get("form_js", {})
                    try:
                        page.fill(form.get("username_selector", "#username"), form["username_value"])
                        page.fill(form.get("password_selector", "#password"), form["password_value"])
                        login_action = form.get("login_action", "Enter")
                        if login_action.lower() == "enter":
                            page.keyboard.press("Enter")
                        else:
                            page.click(login_action)
                    except Exception as e:
                        registrar_log(nombre_rpa, f"[ERROR] Fallo al aplicar autenticación form_js: {e}")
                        raise

                if wait_time > 0:
                    registrar_log(nombre_rpa, f"Esperando {wait_time} ms...")
                    page.wait_for_timeout(wait_time)

                nombre_captura = None
                if capturar:
                    nombre_captura = f"captura_{idx + 1}_{safe_timestamp}.png"
                    path = os.path.join(screenshot_dir, nombre_captura)
                    full_page = rpa_data.get("pantalla", {}).get("captura_pagina_completa", True)
                    page.screenshot(path=path, full_page=full_page)
                    capturas.append((url_actual, path))
                    registrar_log(nombre_rpa, f"Captura tomada: {path}")

                detalles.append({
                    "url": url_actual,
                    "tiempo_carga": tiempo_carga,
                    "nombre_captura": nombre_captura
                })

    return capturas, detalles