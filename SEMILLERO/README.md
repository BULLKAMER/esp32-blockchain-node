# 🌱 Seguridad en Sistemas Embebidos para Agricultura de Precisión mediante Blockchain

**Semillero de Investigación GDSPROC — Universidad del Quindío**  
Armenia, Quindío, Colombia

---

## 📋 Descripción

Sistema de seguridad criptográfica para datos IoT agrícolas basado en **blockchain ligera**, implementado sobre hardware embebido de bajo costo. El sistema garantiza la **integridad, autenticidad e inmutabilidad** de las lecturas de sensores generadas en campo, usando SHA-256, firma digital Ed25519 y un mecanismo de notaría local tolerante a fallos.

### Flujo del sistema

```
ESP32 (sensores)
    │
    │  SHA-256 del payload
    │  MQTT → topic: sensor/data
    ▼
Raspberry Pi 4 / 5 (nodo edge)
    │
    ├─ 1. Verificación de integridad (SHA-256)
    ├─ 2. Firma digital (Ed25519)
    └─ 3. Notaría local inmutable (CSV)
    │
    ▼
Dashboard Web (Streamlit)
    └─ Visualización en tiempo real
```

### Hardware utilizado

| Componente | Descripción |
|---|---|
| **ESP32** | Microcontrolador de adquisición de datos |
| **DHT22** | Sensor de temperatura (°C) y humedad relativa (%) |
| **Sensor capacitivo** | Sensor de humedad de suelo (%) |
| **Raspberry Pi 4** | Nodo edge — probado y validado |
| **Raspberry Pi 5** | Nodo edge — probado y validado |

> El sistema fue validado en **ambas plataformas** (Raspberry Pi 4 y Pi 5) confirmando compatibilidad completa.

---

## 🏗️ Estructura del repositorio

```
SEMILLERO/
│
├── simulator/
│   ├── __init__.py
│   └── esp32_sim.py        # Simulador del ESP32 (para pruebas sin hardware)
│
├── edge/
│   ├── __init__.py
│   └── edge_node.py        # Nodo edge: verificación + firma + notaría local
│
├── web/
│   ├── __init__.py
│   └── dashboard.py        # Dashboard Streamlit en tiempo real
│
├── keys/
│   └── .gitkeep            # Carpeta para la clave privada (no se sube a GitHub)
│
├── generate_keys.py        # Script para generar la clave privada Ed25519
├── requirements.txt        # Dependencias Python
├── .gitignore
└── README.md
```

---

## ⚙️ Instalación

### Prerequisitos

- Python 3.10 o superior
- Broker MQTT Mosquitto instalado y corriendo

```bash
# Instalar Mosquitto (Raspberry Pi / Ubuntu)
sudo apt update && sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

### Configuración del entorno

```bash
# 1. Clonar el repositorio
git clone https://github.com/BULLKAMER/esp32-blockchain-node.git
cd esp32-blockchain-node

# 2. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Generar la clave privada Ed25519 (solo la primera vez)
python3 generate_keys.py
```

> ⚠️ **La clave privada (`keys/private_key.pem`) nunca se sube al repositorio.** Está excluida en `.gitignore`.

---

## 🚀 Uso

Abrir **tres terminales** en la carpeta `SEMILLERO/`:

### Terminal 1 — Nodo Edge (Raspberry Pi)

```bash
cd ~/SEMILLERO && source venv/bin/activate
python3 -m edge.edge_node
```

### Terminal 2 — Dashboard Web

```bash
cd ~/SEMILLERO && source venv/bin/activate
streamlit run web/dashboard.py
```

### Terminal 3 — Simulador ESP32

```bash
cd ~/SEMILLERO && source venv/bin/activate
python3 -m simulator.esp32_sim
```

El dashboard estará disponible en `http://localhost:8501` y se actualiza automáticamente cada 2 segundos.

---

## 🔐 Seguridad implementada

| Capa | Mecanismo | Propósito |
|---|---|---|
| **Origen (ESP32)** | SHA-256 del payload | Detectar alteraciones en la transmisión |
| **Nodo Edge** | Verificación SHA-256 | Confirmar integridad antes de procesar |
| **Nodo Edge** | Firma Ed25519 | Garantizar autenticidad y no repudio |
| **Almacenamiento** | Notaría local CSV | Persistencia offline e inmutabilidad local |

### Resultados de pruebas de seguridad

- **Tasa de detección de modificaciones no autorizadas:** 100%
- Cualquier alteración de un bit en el payload es detectada inmediatamente antes de ser registrada.

---

## 📊 Dashboard

El dashboard muestra en tiempo real:

- 🌡️ Temperatura actual (°C)
- 💧 Humedad relativa (%)
- 🌱 Humedad de suelo (%)
- 📈 Gráficas de series de tiempo (últimas 25 lecturas)
- 📜 Libro de actas con recibos de notaría digital

---

## 👥 Equipo

**Semillero GDSPROC — Universidad del Quindío**

| Nombre | Rol |
|---|---|
| Maicol Andrés Escobar Rendón | Investigador semillero |
| Juan Diego Justacaro Carmona | Investigador semillero |
| Adriana Lucia Jojoa Botina | Investigador semillero |
| Hugo Andrés Narváez Calpa | Investigador semillero |
| Jorge Iván Marín Hurtado | Tutor |

---

## 📄 Licencia

MIT License — libre uso académico y de investigación.
