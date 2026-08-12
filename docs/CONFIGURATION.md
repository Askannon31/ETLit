# Konfigurationsanleitung

Diese Dokumentation erklärt alle Konfigurationsoptionen von ETLit im Detail.

## 📋 Übersicht

ETLit verwendet eine Python-basierte Konfiguration in `config/config.py`. Jeder ETL-Prozess besteht aus drei Hauptteilen:

1. **Extraction** - Datenquelle
2. **Transformation** - Datenmanipulation (optional)
3. **Loading** - Ziel

## 🏗️ Grundstruktur

```python
config: dict = {
    "ETL": {
        "processes": [
            {
                "name": "ProzessName",
                "description": "Beschreibung des Prozesses",
                "active": True,  # True = aktiv, False = inaktiv
                "extraction": { ... },
                "transformation": { ... },  # Optional
                "loading": { ... }
            }
        ]
    }
}
```

## 📥 Extraction (Datenquellen)

### 1. Gevis API

Extrahiert Daten aus der Gevis ERP API.

```python
"extraction": {
    "type": "gevisapi",
    "name": "Meine Gevis Quelle",
    "debug": True,  # Speichert Debug-Daten
    
    # Authentifizierung
    "authorization": {
        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
    },
    
    # API-Konfiguration
    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
    "endpoint": "/api/gws/ecm/v1.0/itemLedgerEntries",
    
    # Query-Parameter (optional)
    "query_parameters": {
        "company": "Firmenname",
        "$filter": "systemModifiedAt gt 2025-10-01T11:47:03.117Z",
        "$top": 100,
        "$skip": 0
    },
    
    # Feld-Mapping
    "mapping": {
        "quellfeldName": "zielfeldName",
        "id": "id",
        "documentNo": "no",
        "documentDate": "date"
    }
}
```

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `type` | string | Ja | Muss "gevisapi" sein |
| `name` | string | Ja | Name der Datenquelle |
| `debug` | boolean | Nein | Aktiviert Debug-Ausgabe (Standard: False) |
| `authorization` | object | Ja | Client-Credentials für OAuth2 |
| `erp_tenant_id` | string | Ja | Mandanten-ID |
| `base_url` | string | Ja | Basis-URL der API |
| `endpoint` | string | Ja | API-Endpoint |
| `query_parameters` | object | Nein | URL-Query-Parameter |
| `mapping` | object | Ja | Feld-Zuordnung |

### 2. MSSQL Datenbank

Extrahiert Daten aus einer Microsoft SQL Server Datenbank.

```python
"extraction": {
    "type": "mssql",
    "name": "MSSQL Quelle",
    
    # Verbindungsdaten
    "connection": {
        "server": "dms-dev",  # oder "server\\instance"
        "database": "masterdata",
        "username": os.environ.get("MSSQL_USERNAME"),
        "password": os.environ.get("MSSQL_PASSWORD"),
        "driver": "{ODBC Driver 17 for SQL Server}",  # Optional
        "port": 1433  # Optional
    },
    
    # SQL-Abfrage
    "table": "ETLitTest",  # Optional: Tabellenname
    "query": "SELECT id, name, date FROM ETLitTest WHERE active = 1",
    
    # Feld-Mapping mit Datentypen
    "mapping": [
        {
            "target_field": "id",
            "data_type": "string"
        },
        {
            "target_field": "name",
            "data_type": "string"
        },
        {
            "target_field": "date",
            "data_type": "date"
        }
    ]
}
```

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `type` | string | Ja | Muss "mssql" sein |
| `connection` | object | Ja | Datenbankverbindung |
| `query` | string | Ja | SQL-SELECT Statement |
| `mapping` | array | Ja | Feld-Zuordnung mit Typen |

### 3. PostgreSQL Datenbank

Extrahiert Daten aus einer PostgreSQL Datenbank.

```python
"extraction": {
    "type": "postgres",
    "name": "PostgreSQL Quelle",

    # Verbindungsdaten
    "connection": {
        "host": "localhost",
        "port": 5432,
        "database": "my_database",
        "username": os.environ.get("POSTGRES_USERNAME"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "sslmode": "prefer",          # Optional
        "connect_timeout": 10           # Optional
    },

    # SQL-Abfrage
    "schema": "public",               # Optional
    "table": "my_table",              # Optional wenn query gesetzt ist
    "query": "SELECT id, name FROM public.my_table",

    # Feld-Mapping mit Datentypen
    "mapping": [
        {
            "target_field": "id",
            "data_type": "string"
        },
        {
            "target_field": "name",
            "data_type": "string"
        }
    ]
}
```

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `type` | string | Ja | Muss "postgres" sein |
| `connection` | object | Ja | PostgreSQL-Verbindung |
| `query` | string | Nein | SQL-SELECT Statement (hat Vorrang vor `table`) |
| `table` | string | Nein | Tabellenname (Fallback wenn `query` nicht gesetzt) |
| `schema` | string | Nein | Schema für `table` (Standard: "public") |
| `mapping` | array/object | Ja | Feld-Zuordnung |

### 4. CSV-Datei

Extrahiert Daten aus einer lokalen CSV-Datei.

```python
"extraction": {
    "type": "csvfile",
    "name": "CSV Import",
    "debug": True,
    
    # Dateikonfiguration
    "file_path": "data/input/data.csv",
    "save_path": "data/save",  # Backup nach Verarbeitung
    "delimiter": ";",
    "encoding": "utf-8",
    
    # Spalten-Definition
    "columns": [
        "id",
        "name",
        "date",
        "amount"
    ],
    
    # Feld-Mapping
    "mapping": {
        "id": "id",
        "name": "customerName",
        "date": "orderDate",
        "amount": "totalAmount"
    }
}
```

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `type` | string | Ja | Muss "csvfile" sein |
| `file_path` | string | Ja | Pfad zur CSV-Datei |
| `save_path` | string | Nein | Backup-Verzeichnis |
| `delimiter` | string | Nein | Trennzeichen (Standard: ",") |
| `encoding` | string | Nein | Zeichenkodierung (Standard: "utf-8") |
| `columns` | array | Nein | Spaltennamen (falls keine Header) |
| `mapping` | object | Ja | Feld-Zuordnung |

## 🔄 Transformation

Transformiert Daten zwischen Extraktion und Laden mit Hook-Funktionen.

```python
"transformation": {
    "type": "hookfunction",
    "name": "Datentransformation",
    "description": "Transformiert und validiert Daten",
    "debug": True,
    
    # Hook-Konfiguration
    "hook_file": "scripts/hooks/transform_hooks.py",
    "function_name": "transform_items",
    
    # Zusätzliche Konfiguration für Hook
    "config": {
        "date_format": "%Y-%m-%d",
        "currency": "EUR",
        "validation_rules": {
            "id": "required",
            "amount": "numeric"
        }
    }
}
```

**Beispiel Hook-Funktion** (`scripts/hooks/transform_hooks.py`):

```python
def transform_items(items: list, config: dict) -> list:
    """
    Transformiert die extrahierten Items.
    
    Args:
        items: Liste der zu transformierenden Items
        config: Konfiguration aus der transformation.config
    
    Returns:
        Liste der transformierten Items
    """
    transformed = []
    
    for item in items:
        # Datum formatieren
        if 'date' in item:
            item['date'] = format_date(item['date'], config.get('date_format'))
        
        # Währung hinzufügen
        if 'amount' in item:
            item['currency'] = config.get('currency', 'EUR')
        
        # Validierung
        if validate_item(item, config.get('validation_rules', {})):
            transformed.append(item)
        else:
            print(f"Item {item.get('id')} failed validation")
    
    return transformed
```

## 📤 Loading (Ziele)

### 1. D3 Business Objects

Lädt Daten in D3 Business Objects mit Batch-Unterstützung.

```python
"loading": {
    "type": "d3businessobjects",
    "name": "D3 Upload",
    
    # API-Konfiguration
    "base_url": os.environ.get("D3_API_BASE_URL"),
    "api_key": os.environ.get("D3_API_KEY"),
    
    # Batch-Konfiguration
    "batch_size": 100,  # Max. 100 Items pro Batch
    
    # Modell und Entity
    "model": "latescanning",
    "truncate_before_load": False,  # Löscht vorhandene Daten
    
    # Entity-Definition
    "entity": {
        "name": "ItemLedgerEntry",
        "plural": "ItemLedgerEntries",
        
        # Entity-Schema
        "definition": {
            "name": "ItemLedgerEntry",
            "pluralName": "ItemLedgerEntries",
            "description": "ItemLedgerEntries entity type",
            "state": "published",
            
            # Primärschlüssel
            "key": {
                "name": "id",
                "type": "string",  # string, int32, int64, guid
                "state": "published"
            },
            
            # Eigenschaften
            "properties": [
                {
                    "name": "no",
                    "type": "string",
                    "state": "published"
                },
                {
                    "name": "documentDate",
                    "type": "date",
                    "state": "published"
                },
                {
                    "name": "amount",
                    "type": "decimal",
                    "state": "published"
                }
            ]
        }
    },
    
    # Feld-Mapping
    "mapping": {
        "id": "id",
        "no": "no",
        "date": "documentDate",
        "amount": "amount"
    }
}
```

**Unterstützte Datentypen:**
- `string` - Text
- `int32` - 32-Bit Integer
- `int64` - 64-Bit Integer
- `decimal` - Dezimalzahl
- `double` - Fließkommazahl
- `boolean` - true/false
- `date` - Datum (ISO 8601)
- `datetime` - Datum mit Zeit
- `guid` - GUID/UUID

**Parameter:**

| Parameter | Typ | Erforderlich | Beschreibung |
|-----------|-----|--------------|--------------|
| `type` | string | Ja | Muss "d3businessobjects" sein |
| `base_url` | string | Ja | D3 Instanz URL |
| `api_key` | string | Ja | API-Schlüssel |
| `batch_size` | integer | Nein | Items pro Batch (Standard: 100, Max: 100) |
| `model` | string | Ja | Modellname |
| `truncate_before_load` | boolean | Nein | Daten vorher löschen (Standard: False) |
| `entity` | object | Ja | Entity-Definition |
| `mapping` | object | Ja | Feld-Zuordnung |

### 2. MSSQL Datenbank

Lädt Daten in eine Microsoft SQL Server Datenbank.

```python
"loading": {
    "type": "mssql",
    "name": "MSSQL Insert",
    
    # Verbindungsdaten
    "connection": {
        "server": "dms-dev",
        "database": "masterdata",
        "username": os.environ.get("MSSQL_USERNAME"),
        "password": os.environ.get("MSSQL_PASSWORD")
    },
    
    # Ziel-Tabelle
    "table": "ETLitTest",
    
    # INSERT Statement mit Platzhaltern
    "insert_statement": """
        INSERT INTO ETLitTest (
            id, lfdNr, no, date, dokuid, account, costaccount, company
        ) VALUES (
            '@TargetField1', '@TargetField2', '@TargetField3', '@TargetField4',
            '@TargetField5', '@TargetField6', '@TargetField7', '@TargetField8'
        )
    """,
    
    # Feld-Mapping zu Platzhaltern
    "mappings": {
        "id": "TargetField1",
        "lfdNr": "TargetField2",
        "no": "TargetField3",
        "date": "TargetField4",
        "dokuid": "TargetField5",
        "account": "TargetField6",
        "costaccount": "TargetField7",
        "company": "TargetField8"
    }
}
```

## 🔧 Erweiterte Konfiguration

### Mehrere Prozesse

Du kannst mehrere ETL-Prozesse in einer Config definieren:

```python
config: dict = {
    "ETL": {
        "processes": [
            {
                "name": "Prozess 1",
                "active": True,
                # ...
            },
            {
                "name": "Prozess 2",
                "active": False,  # Inaktiv
                # ...
            },
            {
                "name": "Prozess 3",
                "active": True,
                # ...
            }
        ]
    }
}
```

### Umgebungsspezifische Konfiguration

Verwende Umgebungsvariablen für verschiedene Umgebungen:

```python
import os

environment = os.environ.get("ENVIRONMENT", "development")

if environment == "production":
    base_url = "https://prod-api.example.com"
    batch_size = 100
elif environment == "staging":
    base_url = "https://stage-api.example.com"
    batch_size = 50
else:  # development
    base_url = "https://dev-api.example.com"
    batch_size = 10

config = {
    "ETL": {
        "processes": [{
            "loading": {
                "base_url": base_url,
                "batch_size": batch_size
            }
        }]
    }
}
```

### Debug-Modus

Debug-Modus aktivieren für detaillierte Ausgaben:

```python
"extraction": {
    "debug": True  # Speichert Daten in debug/ Ordner
}

"transformation": {
    "debug": True  # Zeigt Transformation-Details
}
```

Debug-Dateien werden gespeichert als:
```
debug/{name}_{timestamp}_debug_data.json
debug/{name}_{timestamp}_debug_mapped_data.json
```

## 📝 Best Practices

### 1. Credentials nicht im Code

❌ **Schlecht:**
```python
"api_key": "mein-geheimer-key-123"
```

✅ **Gut:**
```python
"api_key": os.environ.get("D3_API_KEY")
```

### 2. Sinnvolle Namen verwenden

✅ **Gut:**
```python
"name": "Gevis_ItemLedgerEntries_to_D3_Daily"
"description": "Täglicher Import von Item Ledger Entries aus Gevis in D3"
```

### 3. Batch-Größe optimieren

```python
# Für große Datenmengen
"batch_size": 100  # Maximum

# Für Tests/Development
"batch_size": 10
```

### 4. Mappings dokumentieren

```python
"mapping": {
    "sourceField1": "targetField1",  # Kunden-ID
    "sourceField2": "targetField2",  # Bestellnummer
    "sourceField3": "targetField3"   # Bestelldatum
}
```

### 5. Fehlerbehandlung

```python
"loading": {
    "truncate_before_load": False,  # Sichere Variante
    "batch_size": 50,  # Kleinere Batches bei Problemen
}
```

## 🔍 Konfiguration validieren

Erstelle ein Test-Script `validate_config.py`:

```python
import json
from config.config import config

def validate_config():
    for process in config["ETL"]["processes"]:
        print(f"Validating: {process['name']}")
        
        # Prüfe erforderliche Felder
        required_fields = ["name", "extraction", "loading"]
        for field in required_fields:
            if field not in process:
                print(f"  ERROR: Missing field '{field}'")
                return False
        
        # Prüfe Extraction-Type
        valid_extraction_types = ["gevisapi", "mssql", "postgres", "csvfile"]
        if process["extraction"]["type"] not in valid_extraction_types:
            print(f"  ERROR: Invalid extraction type")
            return False
        
        print(f"  OK")
    
    return True

if __name__ == "__main__":
    if validate_config():
        print("\n✓ Configuration is valid")
    else:
        print("\n✗ Configuration has errors")
```

## 🆘 Hilfe bei Konfigurationsproblemen

Siehe auch:
- [Installation](INSTALLATION.md)
- [Beispiele](EXAMPLES.md)
- [API-Referenz](API.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Tipp**: Verwende JSON Schema für Validierung und Auto-Completion in deiner IDE!
