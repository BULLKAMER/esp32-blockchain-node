"""
Simulador del Nodo ESP32
========================
Simula la captura de datos de sensores reales (DHT22 y sensor de humedad de suelo)
y los publica via MQTT hacia el nodo edge (Raspberry Pi).

Cada paquete incluye un sello SHA-256 calculado en origen para garantizar
la integridad del dato durante la transmisión.

Sensores simulados:
  - DHT22: temperatura (°C) y humedad relativa (%)
  - Sensor capacitivo de humedad de suelo (%)

Uso:
    python3 -m simulator.esp32_sim
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import hashlib

# ── Configuración del broker MQTT ──────────────────────────────────────────────
BROKER = "127.0.0.1"
PORT   = 1883
TOPIC  = "sensor/data"


def generate_data() -> tuple[dict, str]:
    """
    Genera una lectura de sensores y su hash SHA-256.

    Returns:
        sensor_data: diccionario con temp, hum, soil_hum y timestamp.
        data_hash:   huella digital SHA-256 del payload.
    """
    sensor_data = {
        "temp":      round(random.uniform(20.0, 35.0), 2),   # DHT22 – temperatura (°C)
        "hum":       round(random.uniform(40.0, 80.0), 2),   # DHT22 – humedad relativa (%)
        "soil_hum":  round(random.uniform(10.0, 90.0), 2),   # Sensor capacitivo de suelo (%)
        "timestamp": time.time(),
    }

    data_string = json.dumps(sensor_data, sort_keys=True)
    data_hash   = hashlib.sha256(data_string.encode()).hexdigest()

    return sensor_data, data_hash


# ── Cliente MQTT ───────────────────────────────────────────────────────────────
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

try:
    client.connect(BROKER, PORT, 60)
    print(f"🚀 Simulador ESP32 conectado al broker en {BROKER}:{PORT}")

    while True:
        sensor_data, data_hash = generate_data()

        packet = json.dumps({"data": sensor_data, "hash": data_hash})
        client.publish(TOPIC, packet)

        print(
            f"📡 Enviado → Temp: {sensor_data['temp']}°C | "
            f"Hum: {sensor_data['hum']}% | "
            f"Suelo: {sensor_data['soil_hum']}% | "
            f"Hash: {data_hash[:12]}..."
        )

        time.sleep(2)

except KeyboardInterrupt:
    print("\n⏹️  Simulador detenido.")
except Exception as e:
    print(f"❌ Error al conectar con el broker: {e}")
finally:
    client.disconnect()
