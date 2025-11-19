# Installation & Setup Guide

Diese Anleitung führt dich Schritt für Schritt durch die Installation und Einrichtung von ETLit.

## 📋 Systemanforderungen

### Betriebssystem
- Windows 10/11
- Linux (Ubuntu 20.04+, Debian 10+)
- macOS 10.15+

### Software
- Python 3.10 oder höher
- pip 21.0 oder höher
- Git (optional, für Klonen des Repositories)

### Speicherplatz
- Mindestens 100 MB freier Speicherplatz
- Zusätzlicher Speicher für Logs und Debug-Daten

## 🔧 Installation

### Methode 1: Installation via Git (empfohlen)

#### Schritt 1: Repository klonen

```bash
git clone https://github.com/Askannon31/ETLit.git
cd ETLit
```

#### Schritt 2: Virtuelle Umgebung erstellen

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Schritt 3: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Methode 2: Manuelle Installation

#### Schritt 1: Projekt herunterladen

Lade das Projekt als ZIP-Datei herunter und entpacke es.

#### Schritt 2: In das Verzeichnis wechseln

```bash
cd ETLit
```

#### Schritt 3: Virtuelle Umgebung und Abhängigkeiten

Siehe Methode 1, Schritt 2 und 3.

## ⚙️ Konfiguration

### 1. Umgebungsvariablen einrichten

Erstelle eine `.env` Datei im Hauptverzeichnis des Projekts:

```bash
# Windows
notepad .env

# Linux/macOS
nano .env
```

Füge folgende Variablen hinzu:

```env
# ===== Gevis API Konfiguration =====
GEVIS_API_CLIENT_ID=your_client_id_here
GEVIS_API_CLIENT_SECRET=your_client_secret_here
GEVIS_API_ERP_TENANT_ID=your_tenant_id_here
GEVIS_API_BASE_URL=https://api.gevis.de

# ===== D3 Business Objects Konfiguration =====
D3_API_BASE_URL=https://your-d3-instance.com
D3_API_KEY=your_api_key_here

# ===== MSSQL Konfiguration =====
MSSQL_USERNAME=your_database_username
MSSQL_PASSWORD=your_database_password

# ===== Optionale Einstellungen =====
# DEBUG_MODE=True
# LOG_LEVEL=DEBUG
```

### 2. Umgebungsvariablen laden

ETLit lädt automatisch die `.env` Datei, wenn du `python-dotenv` installiert hast:

```bash
pip install python-dotenv
```

Füge dann in `config/config.py` am Anfang hinzu:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. Logging konfigurieren

Die Logging-Konfiguration findest du in `config/logging.json`:

```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "default": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "default"
    },
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "formatter": "default",
      "filename": "logs/logging.log",
      "maxBytes": 10485760,
      "backupCount": 5
    }
  },
  "root": {
    "level": "DEBUG",
    "handlers": ["console", "file"]
  }
}
```

## 🗂️ Verzeichnisstruktur erstellen

ETLit erstellt automatisch benötigte Verzeichnisse. Du kannst sie auch manuell erstellen:

```bash
# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path logs, debug, data/input, data/output, data/save

# Linux/macOS
mkdir -p logs debug data/input data/output data/save
```

## ✅ Installation überprüfen

### Test 1: Python-Version prüfen

```bash
python --version
# Sollte ausgeben: Python 3.10.x oder höher
```

### Test 2: Abhängigkeiten prüfen

```bash
pip list
```

Prüfe, ob folgende Pakete installiert sind:
- requests
- pyodbc (für MSSQL)
- python-dotenv (optional)

### Test 3: ETLit starten

```bash
python main.py
```

Wenn alles korrekt installiert ist, solltest du Ausgaben wie diese sehen:

```
2025-11-19 10:00:00 - INFO - Starting ETL process: MeinETLProzess
2025-11-19 10:00:00 - INFO - Initialized ETLExtractGevisApi with name: Delbrueck Item Ledger Entries
...
```

## 🔐 Sicherheitshinweise

### .env Datei schützen

**Wichtig**: Füge `.env` zu deiner `.gitignore` hinzu, um Credentials nicht zu committen:

```bash
echo ".env" >> .gitignore
```

### Dateiberechtigungen (Linux/macOS)

```bash
chmod 600 .env
chmod 700 logs/
chmod 700 debug/
```

## 🚀 Erste Schritte nach der Installation

### 1. Teste die Verbindungen

Teste zuerst die Verbindungen zu deinen Datenquellen:

```python
# test_connection.py
import os
import requests

# Test Gevis API
def test_gevis_api():
    base_url = os.getenv("GEVIS_API_BASE_URL")
    print(f"Testing connection to: {base_url}")
    # ... Test-Code

# Test D3 API
def test_d3_api():
    base_url = os.getenv("D3_API_BASE_URL")
    api_key = os.getenv("D3_API_KEY")
    print(f"Testing connection to: {base_url}")
    # ... Test-Code

if __name__ == "__main__":
    test_gevis_api()
    test_d3_api()
```

### 2. Konfiguriere deinen ersten ETL-Prozess

Bearbeite `config/config.py` und setze einen Prozess auf `active: True`.

### 3. Starte den ETL-Prozess

```bash
python main.py
```

## 🔧 Fehlerbehebung

### Problem: ModuleNotFoundError

**Lösung**: Stelle sicher, dass die virtuelle Umgebung aktiviert ist:

```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate
```

Dann installiere die Abhängigkeiten erneut:

```bash
pip install -r requirements.txt
```

### Problem: Keine Verbindung zur Datenbank

**Lösung**: Prüfe:
1. MSSQL Server läuft
2. Firewall-Einstellungen
3. Credentials in `.env`

```bash
# Test MSSQL Verbindung
python -c "import pyodbc; print(pyodbc.drivers())"
```

### Problem: API-Authentifizierung schlägt fehl

**Lösung**: 
1. Prüfe API-Keys in `.env`
2. Prüfe, ob die API erreichbar ist:

```bash
curl -I https://api.gevis.de
```

### Problem: Permission Denied (Linux/macOS)

**Lösung**: Setze die richtigen Berechtigungen:

```bash
chmod +x main.py
chmod -R 755 scripts/
```

## 🔄 Updates

### ETLit aktualisieren

Wenn du via Git installiert hast:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Abhängigkeiten aktualisieren

```bash
pip list --outdated
pip install --upgrade <package-name>
```

## 📦 Deployment

### Produktionsumgebung

Für den Produktivbetrieb:

1. **Verwende einen dedizierten User**:
```bash
sudo useradd -m -s /bin/bash etlit
sudo su - etlit
```

2. **Installiere als Service (Linux)**:

Erstelle `/etc/systemd/system/etlit.service`:

```ini
[Unit]
Description=ETLit Service
After=network.target

[Service]
Type=simple
User=etlit
WorkingDirectory=/home/etlit/ETLit
Environment="PATH=/home/etlit/ETLit/venv/bin"
ExecStart=/home/etlit/ETLit/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktiviere den Service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable etlit
sudo systemctl start etlit
```

3. **Verwende einen Scheduler**:

**Windows (Task Scheduler)**:
- Öffne Task Scheduler
- Erstelle neue Task
- Trigger: Täglich/Stündlich
- Action: `python.exe` mit Pfad zu `main.py`

**Linux (Cron)**:
```bash
crontab -e
# Täglich um 2:00 Uhr
0 2 * * * /home/etlit/ETLit/venv/bin/python /home/etlit/ETLit/main.py
```

## 🆘 Support

Bei Installationsproblemen:

1. Prüfe die [FAQ](FAQ.md)
2. Schaue in die [Troubleshooting-Sektion](TROUBLESHOOTING.md)
3. Öffne ein Issue auf GitHub

## 📝 Nächste Schritte

Nach erfolgreicher Installation:

- Lies die [Konfigurationsanleitung](CONFIGURATION.md)
- Schaue dir die [Beispiele](EXAMPLES.md) an
- Erkunde die [API-Referenz](API.md)

---

**Tipp**: Erstelle regelmäßig Backups deiner Konfiguration und `.env` Datei!
