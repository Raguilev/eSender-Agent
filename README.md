# eSender Agent 📨

**eSender Agent** es una aplicación de escritorio ligera desarrollada en Python con PyQt5, diseñada para ejecutar RPAs (automatizaciones) configuradas previamente mediante archivos cifrados (`.enc`). El agente permite programar, gestionar, ejecutar manualmente y visualizar el historial de ejecuciones de múltiples RPAs de forma local y segura, sin necesidad de depender del Task Scheduler del sistema operativo.

## 🧩 Características principales

- ✅ Carga y gestión de RPAs cifrados (.enc + .key)
- ✅ Ejecución programada (hourly, daily, weekly) según configuración JSON
- ✅ Indicadores visuales de RPAs activos e inactivos
- ✅ Ejecución manual bajo demanda con un clic
- ✅ Visualización de logs de ejecución con resumen detallado
- ✅ Sistema modular y cifrado AES-256 para máxima seguridad
- ✅ Interfaz gráfica intuitiva con PyQt5

---

## 📁 Estructura del proyecto

```
eSender_AGENT/
├── agent_runner.py             # Punto de entrada principal (.exe)
├── core/                       # Lógica funcional del agente
│   ├── crypto_utils.py         # Módulo de descifrado AES
│   ├── log_handler.py          # Módulo de gestión de logs
│   ├── mail_sender.py          # Envío de correos con capturas embebidas
│   ├── navigator.py            # Navegación y captura con Playwright
│   ├── rpa_executor.py         # Ejecución del flujo completo de RPA
│   ├── rpa_manager.py          # Gestión de RPAs cargados
│   └── scheduler.py            # Programación horaria de RPAs
├── logs_rpa/                   # Carpeta de logs por RPA (autogenerada)
├── Reportes/                   # Capturas generadas por los RPAs (autogenerada)
├── rpas_cargados/              # RPAs cargados localmente (.enc + .key + meta)
├── ui/                         # Interfaz gráfica
│   ├── agent_window.py         # Ventana principal del agente
│   └── tray_icon.py            # Lógica de ejecución en bandeja del sistema
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Este archivo
```

---

## 🚀 Requisitos

- Python 3.9 o superior
- Sistema operativo: Windows / macOS
- Navegador compatible con Playwright instalado (por ejemplo, Chromium)

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

---

## 🔐 Estructura de un RPA cifrado

Cada RPA debe estar compuesto por los siguientes elementos:

```
nombre_rpa/
├── rpa_config.enc     # Archivo de configuración cifrada (AES-256)
├── rpa.key            # Clave secreta (32 bytes)
└── meta.json          # Información adicional (descripción, fecha, ejecuciones)
```

---

## 🖥 Uso de la interfaz

1. **Cargar RPA**: Selecciona un archivo `.enc` y su respectivo `.key`, asigna un nombre y una descripción opcional.
2. **Activar/Inactivar**: Cambia el estado de un RPA para que se ejecute automáticamente según la programación definida.
3. **▶ Ejecutar ahora**: Forzar la ejecución inmediata de un RPA, útil para pruebas.
4. **Logs**: Visualiza los eventos detallados de ejecución por RPA en la pestaña `Resumen de Logs`.

---

## 📅 Programación de RPAs

Cada RPA puede ser programado con la siguiente estructura:

```json
"programacion": {
  "frecuencia": "hourly",      // o "daily", "weekly"
  "intervalo": 1,              // Cada cuántas unidades ejecutar
  "hora_inicio": "08:00"       // Hora inicial de ejecución
}
```

El agente se encarga de ejecutar automáticamente los RPAs activos según esta configuración.

---

## 🛠 Empaquetado como .exe

Para generar el ejecutable:

```bash
pyinstaller --onefile --windowed --name "eSender_agent" agent_runner.py
```

También puedes personalizar el ícono con:

```bash
pyinstaller --onefile --windowed --icon=icono.ico agent_runner.py
```

---

## 📌 Estado del desarrollo

- [x] Lógica de ejecución completa
- [x] Sistema de logs individual por RPA
- [x] Programación con scheduler propio
- [x] Interfaz gráfica modular
- [ ] Modo bandeja completamente funcional en Windows/macOS

---

## 🧑‍💻 Autor

**Raúl G. Lévano Cutiño**  
Facultad de Ingeniería - Universidad de Lima  
Proyecto de automatización segura con ejecución programada local

---

## 📄 Licencia

Este proyecto es de uso académico. Para usos comerciales o empresariales, contactar al autor.
