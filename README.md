# ETLit - ETL Tool für Python

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

ETLit ist ein flexibles ETL (Extract, Transform, Load) Tool in Python, das entwickelt wurde, um Daten aus verschiedenen Quellen zu extrahieren, zu transformieren und in verschiedene Zielsysteme zu laden.

## 📋 Inhaltsverzeichnis

- [Features](#features)
- [Unterstützte Systeme](#unterstützte-systeme)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dokumentation](#dokumentation)
- [Konfiguration](#konfiguration)
- [Beispiele](#beispiele)
- [Lizenz](#lizenz)

## ✨ Features

- **Modulare Architektur**: Einfach erweiterbar mit neuen Quellen und Zielen
- **Multiple Datenquellen**: Unterstützung für APIs, Datenbanken, CSV-Dateien und mehr
- **Batch-Verarbeitung**: Effiziente Verarbeitung großer Datenmengen
- **Transformation Hooks**: Flexible Datenmanipulation durch Hook-Funktionen
- **Umfangreiches Logging**: Detaillierte Logs für Debugging und Monitoring
- **Debug-Modus**: Speichert Zwischen-Daten für Analyse und Fehlersuche
- **Konfigurationsbasiert**: JSON-basierte Konfiguration für alle ETL-Prozesse

## 🔌 Unterstützte Systeme

### Datenquellen (Extract)
- **Gevis API**: Extraktion aus der Gevis ERP API
- **MSSQL**: Microsoft SQL Server Datenbank
- **CSV-Dateien**: Lokale CSV-Dateien

### Ziele (Load)
- **D3 Business Objects**: Upload zu D3 Business Objects API mit Batch-Unterstützung
- **MSSQL**: Microsoft SQL Server Datenbank

## 📦 Installation

### Voraussetzungen

- Python 3.10 oder höher
- pip (Python Package Manager)

### Schritt 1: Repository klonen

```bash
git clone https://github.com/Askannon31/ETLit.git
cd ETLit
```

### Schritt 2: Virtuelle Umgebung erstellen (empfohlen)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Schritt 3: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Umgebungsvariablen konfigurieren

Erstelle eine `.env` Datei im Hauptverzeichnis:

```env
# Gevis API
GEVIS_API_CLIENT_ID=your_client_id
GEVIS_API_CLIENT_SECRET=your_client_secret
GEVIS_API_ERP_TENANT_ID=your_tenant_id
GEVIS_API_BASE_URL=https://api.gevis.de

# D3 Business Objects
D3_API_BASE_URL=https://your-d3-instance.com
D3_API_KEY=your_api_key

# MSSQL
MSSQL_USERNAME=your_username
MSSQL_PASSWORD=your_password
```

## 🚀 Quick Start

### Einfaches Beispiel

1. **Konfiguration erstellen** (siehe `config/config.py`)
2. **ETL-Prozess starten**:

```bash
python main.py
```

Standardmäßig wird `config/config.py` geladen. Für eine andere Konfiguration
kann der Dateiname aus dem Ordner `config` als Argument übergeben werden:

```bash
python main.py config_production.py
```

### Beispiel-Konfiguration

```python
{
    "name": "MeinETLProzess",
    "active": True,
    "extraction": {
        "type": "gevisapi",
        "name": "Datenabruf von Gevis",
        # ... weitere Konfiguration
    },
    "transformation": {
        "type": "hookfunction",
        # ... Transformation-Hooks
    },
    "loading": {
        "type": "d3businessobjects",
        # ... Zielkonfiguration
    }
}
```

## 📚 Dokumentation

Detaillierte Dokumentation findest du in den folgenden Dateien:

- [**Installation & Setup**](docs/INSTALLATION.md) - Detaillierte Installationsanleitung
- [**Konfiguration**](docs/CONFIGURATION.md) - Vollständige Konfigurationsreferenz
- [**API-Referenz**](docs/API.md) - Technische API-Dokumentation
- [**Beispiele**](docs/EXAMPLES.md) - Vollständige Beispiele für verschiedene Szenarien

## ⚙️ Konfiguration

ETLit verwendet eine zentrale Konfigurationsdatei `config/config.py`. Jeder ETL-Prozess besteht aus drei Hauptkomponenten:

### 1. Extraction (Datenquelle)
```python
"extraction": {
    "type": "gevisapi",
    "name": "Meine Datenquelle",
    "debug": True,
    # ... spezifische Konfiguration
}
```

### 2. Transformation (optional)
```python
"transformation": {
    "type": "hookfunction",
    "hook_file": "scripts/hooks/transform_hooks.py",
    "function_name": "transform_items"
}
```

### 3. Loading (Ziel)
```python
"loading": {
    "type": "d3businessobjects",
    "name": "Mein Ziel",
    "batch_size": 100,
    # ... spezifische Konfiguration
}
```

## 📖 Beispiele

### Beispiel 1: CSV zu D3 Business Objects

```python
{
    "name": "CSV Upload",
    "active": True,
    "extraction": {
        "type": "csvfile",
        "file_path": "data/input/data.csv",
        "delimiter": ";"
    },
    "loading": {
        "type": "d3businessobjects",
        "batch_size": 100,
        "model": "mymodel"
    }
}
```

### Beispiel 2: Gevis API zu MSSQL

```python
{
    "name": "API zu Datenbank",
    "active": True,
    "extraction": {
        "type": "gevisapi",
        "endpoint": "/api/gws/ecm/v1.0/itemLedgerEntries"
    },
    "loading": {
        "type": "mssql",
        "table": "MyTable"
    }
}
```

Weitere Beispiele findest du in der [Beispiel-Dokumentation](docs/EXAMPLES.md).

## 🐛 Debug-Modus

ETLit bietet einen Debug-Modus, der Zwischendaten speichert:

```python
"extraction": {
    "debug": True,  # Speichert extrahierte Daten in debug/
}
```

Debug-Dateien werden im `debug/` Verzeichnis gespeichert.

## 📊 Logging

Logs werden in `logs/logging.log` gespeichert. Die Logging-Konfiguration befindet sich in `config/logging.json`.

### Log-Level
- **INFO**: Allgemeine Informationen
- **DEBUG**: Detaillierte Debug-Informationen
- **WARNING**: Warnungen
- **ERROR**: Fehler

## 🔧 Entwicklung

### Projekt-Struktur

```
ETLit/
├── config/              # Konfigurationsdateien
│   ├── config.py       # Hauptkonfiguration
│   └── logging.json    # Logging-Konfiguration
├── scripts/
│   ├── classes/        # ETL-Klassen
│   │   ├── ETLExtract/ # Extraktions-Klassen
│   │   └── ETLLoad/    # Lade-Klassen
│   ├── hooks/          # Transformation-Hooks
│   └── utils/          # Hilfsfunktionen
├── logs/               # Log-Dateien
├── debug/              # Debug-Ausgaben
├── main.py            # Hauptprogramm
└── README.md          # Diese Datei
```

### Neue Datenquelle hinzufügen

1. Erstelle eine neue Klasse in `scripts/classes/ETLExtract/`
2. Erbe von `ETLExtractBase`
3. Implementiere die `extract()` Methode
4. Registriere die Klasse in der Factory

Siehe [API-Dokumentation](docs/API.md) für Details.

## 🤝 Beiträge

Beiträge sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.

## 🆘 Support

Bei Fragen oder Problemen:

1. Prüfe die [Dokumentation](docs/)
2. Schaue in die [Beispiele](docs/EXAMPLES.md)
3. Öffne ein Issue auf GitHub

## 👥 Autoren

- **Askannon31** - *Initial work* - [GitHub](https://github.com/Askannon31)

## 🙏 Danksagungen

- D3 Business Objects Team
- Gevis API Team
- Alle Mitwirkenden

---

**Hinweis**: Diese Software wird "wie besehen" bereitgestellt, ohne jegliche Garantie.
