"""
Generador de Clave Privada Ed25519
====================================
Crea una clave privada de 32 bytes aleatorios en keys/private_key.pem.
Ejecutar UNA sola vez antes de arrancar el sistema por primera vez.

Uso:
    python3 generate_keys.py
"""

import os
from pathlib import Path

KEY_PATH = Path(__file__).parent / "keys" / "private_key.pem"

def generate():
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if KEY_PATH.exists():
        print(f"⚠️  La clave ya existe en {KEY_PATH}")
        confirm = input("¿Sobreescribir? Esto invalidará recibos anteriores [s/N]: ").strip().lower()
        if confirm != "s":
            print("Operación cancelada.")
            return

    key_bytes = os.urandom(32)
    KEY_PATH.write_bytes(key_bytes)
    print(f"✅ Clave privada generada en: {KEY_PATH}")
    print(f"   Tamaño: {len(key_bytes)} bytes")
    print("⚠️  IMPORTANTE: No compartas ni subas este archivo a GitHub.")

if __name__ == "__main__":
    generate()
