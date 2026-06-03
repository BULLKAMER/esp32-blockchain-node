"""
Nodo Edge — Cerebro Criptográfico (Raspberry Pi 4 / Pi 5)
==========================================================
Recibe los datos del ESP32 via MQTT y ejecuta tres operaciones secuenciales:

  1. Verificación de integridad SHA-256:
       Recalcula el hash del payload y lo compara con el hash enviado por
       el ESP32. Cualquier alteración durante la transmisión es detectada.

  2. Firma digital Ed25519:
       Firma criptográficamente el paquete verificado con la clave privada
       del nodo, garantizando autenticidad y no repudio del dato.

  3. Notaría local inmutable (modo offline):
       Genera un recibo digital SHA-256 del paquete firmado y lo almacena
       en un archivo CSV local como respaldo ante pérdida de conectividad.

Probado en: Raspberry Pi 4 y Raspberry Pi 5
Protocolo:  MQTT (broker Mosquitto, puerto 1883)

Uso:
    python3 -m edge.edge_node
"""

import paho.mqtt.client as mqtt
import json
import hashlib
import csv
from datetime import datetime
from pathlib import Path
from loguru import logger
from cryptography.hazmat.primitives.asymmetric import ed25519

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent.parent
KEY_PATH     = BASE_DIR / "keys" / "private_key.pem"
DATA_CSV     = BASE_DIR / "data.csv"

# ── ID del nodo (cambiar si se despliegan múltiples nodos) ─────────────────────
NODE_ID = "RPI-ARMENIA-01"


def load_private_key() -> ed25519.Ed25519PrivateKey:
    """Carga la clave privada Ed25519 de 32 bytes desde disco."""
    key_data = KEY_PATH.read_bytes().strip()
    if len(key_data) != 32:
        raise ValueError(
            f"La clave debe tener exactamente 32 bytes. "
            f"Encontrados: {len(key_data)}. "
            f"Ejecuta: python3 -c \"import os; open('keys/private_key.pem','wb').write(os.urandom(32))\""
        )
    return ed25519.Ed25519PrivateKey.from_private_bytes(key_data)


private_key = load_private_key()


def save_to_csv(timestamp: str, temp: float, hum: float, soil_hum: float, receipt: str) -> None:
    """Persiste un registro en el CSV local (crea el archivo si no existe)."""
    write_header = not DATA_CSV.exists()
    with DATA_CSV.open("a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Hora", "Temperatura", "Humedad", "Humedad_Suelo", "Recibo_Notarial"])
        writer.writerow([timestamp, temp, hum, soil_hum, receipt[:16] + "..."])


def on_message(client, userdata, msg) -> None:
    """Callback ejecutado al recibir un mensaje MQTT."""
    try:
        payload       = json.loads(msg.payload.decode())
        data          = payload["data"]
        received_hash = payload["hash"]

        # ── 1. Verificación de integridad ──────────────────────────────────────
        computed_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

        if computed_hash != received_hash:
            logger.error("🚨 ALERTA: Hash no coincide. Dato corrupto o manipulado. Descartando.")
            return

        logger.info("✅ Integridad verificada (SHA-256 OK)")

        # ── 2. Firma digital Ed25519 ───────────────────────────────────────────
        signature = private_key.sign(
            json.dumps(payload, sort_keys=True).encode()
        ).hex()

        signed_package = {
            "payload":   payload,
            "signature": signature,
            "node_id":   NODE_ID,
        }
        logger.info(f"🔏 Firma Ed25519 generada por {NODE_ID}")

        # ── 3. Notaría local (respaldo offline) ───────────────────────────────
        receipt = hashlib.sha256(
            json.dumps(signed_package).encode()
        ).hexdigest()

        timestamp = datetime.now().strftime("%H:%M:%S")
        save_to_csv(
            timestamp  = timestamp,
            temp       = data.get("temp",     0),
            hum        = data.get("hum",      0),
            soil_hum   = data.get("soil_hum", 0),
            receipt    = receipt,
        )
        logger.success(f"📜 Recibo archivado: {receipt[:16]}... | {timestamp}")

    except KeyError as e:
        logger.error(f"❌ Campo faltante en el paquete: {e}")
    except Exception as e:
        logger.error(f"❌ Error procesando paquete: {e}")


# ── Cliente MQTT ───────────────────────────────────────────────────────────────
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message

try:
    client.connect("127.0.0.1", 1883, 60)
    client.subscribe("sensor/data")
    logger.info(f"🛡️  Nodo Edge [{NODE_ID}] activo. Esperando datos del ESP32...")
    client.loop_forever()
except KeyboardInterrupt:
    logger.info("⏹️  Nodo Edge detenido.")
except Exception as e:
    logger.critical(f"No se pudo arrancar el nodo edge: {e}")
