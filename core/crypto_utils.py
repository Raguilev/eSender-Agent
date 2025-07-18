import json
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def descifrar_configuracion(ruta_enc: str, ruta_key: str) -> dict:
    try:
        with open(ruta_key, "rb") as f_key:
            key = f_key.read()
        if len(key) != 32:
            raise ValueError("La clave debe tener exactamente 32 bytes para AES-256.")
    except Exception as e:
        raise RuntimeError(f"Error al leer clave: {e}")

    try:
        with open(ruta_enc, "rb") as f_enc:
            raw = f_enc.read()
        if len(raw) < 16:
            raise ValueError("Archivo cifrado inválido o muy corto.")
        
        iv = raw[:16]
        datos_cifrados = raw[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        datos_descifrados = unpad(cipher.decrypt(datos_cifrados), AES.block_size)

        return json.loads(datos_descifrados.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Error al descifrar o interpretar configuración: {e}")
    except Exception as e:
        raise RuntimeError(f"Fallo general durante el descifrado: {e}")