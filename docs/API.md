# API-Referenz

Technische Dokumentation der ETLit API und Klassen.

## 📋 Inhaltsverzeichnis

1. [Architektur-Übersicht](#architektur-übersicht)
2. [Extract-Klassen](#extract-klassen)
3. [Load-Klassen](#load-klassen)
4. [Transformation-Hooks](#transformation-hooks)
5. [Utilities](#utilities)
6. [Eigene Erweiterungen](#eigene-erweiterungen)

---

## Architektur-Übersicht

ETLit basiert auf einer modularen Architektur mit drei Hauptkomponenten:

```
┌─────────────────────────────────────────┐
│         ETL Process Manager             │
│         (main.py)                       │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼────────┐
│   Extract      │  │   Load         │
│   Factory      │  │   Factory      │
└───────┬────────┘  └───────┬────────┘
        │                   │
   ┌────┴─────┬────┐   ┌────┴─────┬────┐
   │          │    │   │          │    │
┌──▼──┐  ┌───▼┐ ┌─▼─┐ ┌▼──┐  ┌───▼┐ ┌─▼─┐
│Gevis│  │MSSQL││CSV│ │D3 │  │MSSQL││...│
└─────┘  └─────┘└───┘ └───┘  └─────┘└───┘
```

---

## Extract-Klassen

### ETLExtractBase

Basis-Klasse für alle Extractions-Klassen.

**Speicherort:** `scripts/classes/ETLExtract/ETLExtractBase.py`

```python
class ETLExtractBase:
    """
    Basis-Klasse für ETL Extract-Operationen.
    """
    
    def __init__(self, config: dict):
        """
        Initialisiert die Extract-Klasse.
        
        Args:
            config (dict): Konfigurationsdictionary
        """
        self.config = config
        self.name = config.get("name", "ETLExtractBase")
        self.debug = config.get("debug", False)
    
    def extract(self) -> dict:
        """
        Extrahiert Daten aus der Quelle.
        
        Returns:
            dict: Dictionary mit 'items' Liste und optionalen Metadaten
            
        Raises:
            NotImplementedError: Muss von Subklassen implementiert werden
        """
        raise NotImplementedError("extract() must be implemented by subclass")
    
    def save_debug_data(self, data: dict, suffix: str = "data"):
        """
        Speichert Debug-Daten in eine JSON-Datei.
        
        Args:
            data (dict): Zu speichernde Daten
            suffix (str): Suffix für Dateinamen
        """
        if self.debug:
            import json
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"debug/{self.name}_{timestamp}_debug_{suffix}.json"
            
            os.makedirs("debug", exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
```

### ETLExtractGevisApi

Extrahiert Daten aus der Gevis API.

**Speicherort:** `scripts/classes/ETLExtract/ETLExtractGevisApi.py`

#### Methoden

##### `__init__(config: dict)`

Initialisiert die Gevis API Extract-Klasse.

**Parameter:**
- `config`: Konfigurationsdictionary mit folgenden Feldern:
  - `authorization`: Dict mit `client_id` und `client_secret`
  - `erp_tenant_id`: ERP Mandanten-ID
  - `base_url`: Basis-URL der API
  - `endpoint`: API-Endpoint
  - `query_parameters`: Optional, Query-Parameter
  - `mapping`: Feld-Zuordnung

##### `get_access_token() -> str`

Holt ein OAuth2 Access Token.

**Returns:**
- `str`: Access Token

**Raises:**
- `Exception`: Bei Authentifizierungsfehler

##### `extract() -> dict`

Extrahiert Daten von der Gevis API.

**Returns:**
- `dict`: Dictionary mit:
  - `items`: Liste der extrahierten Items
  - `count`: Anzahl der Items
  - `nextLink`: Optional, URL für nächste Seite

**Beispiel:**

```python
from scripts.classes.ETLExtract.ETLExtractGevisApi import ETLExtractGevisApi

config = {
    "name": "My Gevis Extract",
    "debug": True,
    "authorization": {
        "client_id": "your_client_id",
        "client_secret": "your_secret"
    },
    "erp_tenant_id": "your_tenant",
    "base_url": "https://api.gevis.de",
    "endpoint": "/api/gws/ecm/v1.0/itemLedgerEntries",
    "mapping": {
        "sourceField": "targetField"
    }
}

extractor = ETLExtractGevisApi(config)
data = extractor.extract()
print(f"Extracted {len(data['items'])} items")
```

### ETLExtractMSSQL

*Noch nicht vollständig dokumentiert - in Entwicklung*

### ETLExtractCSV

*Noch nicht vollständig dokumentiert - in Entwicklung*

---

## Load-Klassen

### ETLLoadBase

Basis-Klasse für alle Load-Klassen.

**Speicherort:** `scripts/classes/ETLLoad/ETLLoadBase.py`

```python
class ETLLoadBase:
    """
    Basis-Klasse für ETL Load-Operationen.
    """
    
    def __init__(self, config: dict):
        """
        Initialisiert die Load-Klasse.
        
        Args:
            config (dict): Konfigurationsdictionary
        """
        self.config = config
        self.name = config.get("name", "ETLLoadBase")
    
    def setup(self) -> bool:
        """
        Führt Setup-Operationen aus (z.B. Tabellen erstellen).
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        return True
    
    def load(self, data: dict) -> bool:
        """
        Lädt Daten ins Ziel.
        
        Args:
            data (dict): Dictionary mit 'items' Liste
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
            
        Raises:
            NotImplementedError: Muss von Subklassen implementiert werden
        """
        raise NotImplementedError("load() must be implemented by subclass")
```

### ETLLoadD3BusinessObjects

Lädt Daten in D3 Business Objects mit Batch-Unterstützung.

**Speicherort:** `scripts/classes/ETLLoad/ETLLoadD3BusinessObjects.py`

#### Eigenschaften

```python
self.name: str              # Name der Load-Operation
self.base_url: str          # D3 Instanz URL
self.api_key: str           # API-Schlüssel
self.model: str             # Modellname
self.model_id: str          # Modell-ID (wird beim Setup ermittelt)
self.entity: dict           # Entity-Definition
self.batch_size: int        # Items pro Batch (max. 100)
```

#### Methoden

##### `setup() -> bool`

Führt Setup-Operationen aus: Prüft Modell und Entity, erstellt Entity falls nötig.

**Returns:**
- `bool`: True bei Erfolg, False bei Fehler

##### `check_model_exists() -> tuple[bool, dict]`

Prüft, ob das Modell existiert.

**Returns:**
- `tuple`: (exists: bool, model_data: dict)

##### `check_entity_exists(model_data: dict) -> tuple[bool, dict]`

Prüft, ob die Entity im Modell existiert.

**Args:**
- `model_data`: Modell-Daten von `check_model_exists()`

**Returns:**
- `tuple`: (exists: bool, entity_data: dict)

##### `create_entity() -> bool`

Erstellt eine neue Entity im Modell.

**Returns:**
- `bool`: True bei Erfolg, False bei Fehler

##### `build_batch_request(items: list, entity_key_field: str, entity_key_type: str) -> list`

Baut Batch-Request-Payload.

**Args:**
- `items`: Liste der Items
- `entity_key_field`: Name des Key-Feldes
- `entity_key_type`: Typ des Keys ("String", "Guid", "Int32", "Int64")

**Returns:**
- `list`: Liste von Request-Objekten

**Request-Objekt-Struktur:**
```python
{
    "id": "1",                          # Fortlaufende ID
    "method": "PUT",                    # HTTP-Methode
    "url": "EntityName('key')",         # Relative URL
    "body": {...},                      # Item-Daten
    "headers": {
        "content-type": "application/json"
    }
}
```

##### `execute_batch_request(requests: list) -> tuple[bool, dict]`

Führt Batch-Request aus.

**Args:**
- `requests`: Liste von Request-Objekten

**Returns:**
- `tuple`: (success: bool, response: dict)

##### `load(data: dict) -> bool`

Hauptmethode zum Laden der Daten.

**Args:**
- `data`: Dictionary mit:
  - `items`: Liste der Items
  - `entity_key_field`: Optional, Name des Key-Feldes (Standard: "id")
  - `entity_key_type`: Optional, Typ des Keys (Standard: "String")

**Returns:**
- `bool`: True bei Erfolg, False bei Fehler

**Beispiel:**

```python
from scripts.classes.ETLLoad.ETLLoadD3BusinessObjects import ETLLoadD3BusinessObjects

config = {
    "name": "D3 Upload",
    "base_url": "https://your-d3-instance.com",
    "api_key": "your_api_key",
    "batch_size": 100,
    "model": "mymodel",
    "entity": {
        "name": "MyEntity",
        "plural": "MyEntities",
        "definition": {
            "name": "MyEntity",
            "pluralName": "MyEntities",
            "state": "published",
            "key": {
                "name": "id",
                "type": "string",
                "state": "published"
            },
            "properties": [
                {"name": "name", "type": "string", "state": "published"}
            ]
        }
    }
}

loader = ETLLoadD3BusinessObjects(config)

# Setup
if loader.setup():
    # Daten laden
    data = {
        "items": [
            {"id": "1", "name": "Item 1"},
            {"id": "2", "name": "Item 2"}
        ],
        "entity_key_field": "id",
        "entity_key_type": "String"
    }
    
    success = loader.load(data)
    print(f"Load successful: {success}")
```

---

## Transformation-Hooks

### Hook-Funktion-Signatur

```python
def transform_function(items: list, config: dict) -> list:
    """
    Transformiert eine Liste von Items.
    
    Args:
        items (list): Liste von Dictionaries (Items)
        config (dict): Konfiguration aus transformation.config
        
    Returns:
        list: Transformierte Liste von Items
    """
    transformed = []
    
    for item in items:
        # Transformation durchführen
        transformed_item = transform_item(item, config)
        transformed.append(transformed_item)
    
    return transformed
```

### Beispiel: Einfache Transformation

```python
# scripts/hooks/simple_transform.py

import logging

log = logging.getLogger(__name__)

def transform_items(items: list, config: dict) -> list:
    """
    Einfache Item-Transformation.
    """
    transformed = []
    
    for item in items:
        # String in Großbuchstaben
        if 'name' in item:
            item['name'] = item['name'].upper()
        
        # Datum formatieren
        if 'date' in item and config.get('date_format'):
            from datetime import datetime
            date_obj = datetime.fromisoformat(item['date'])
            item['date'] = date_obj.strftime(config['date_format'])
        
        # Berechnetes Feld hinzufügen
        if 'price' in item and 'quantity' in item:
            item['total'] = item['price'] * item['quantity']
        
        transformed.append(item)
    
    log.info(f"Transformed {len(transformed)} items")
    return transformed
```

### Beispiel: Komplexe Transformation mit Validierung

```python
# scripts/hooks/advanced_transform.py

import logging
import re
from typing import Dict, List, Tuple

log = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Validiert E-Mail-Adresse"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_item(item: dict, rules: dict) -> Tuple[bool, List[str]]:
    """
    Validiert ein Item gegen Regeln.
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
    errors = []
    
    for field, rule in rules.items():
        value = item.get(field)
        
        if rule == "required" and not value:
            errors.append(f"Field '{field}' is required")
        
        elif rule == "email" and value:
            if not validate_email(value):
                errors.append(f"Invalid email: {value}")
        
        elif rule == "numeric" and value:
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"Field '{field}' must be numeric")
    
    return len(errors) == 0, errors

def transform_with_validation(items: list, config: dict) -> list:
    """
    Transformation mit Validierung.
    """
    validation_rules = config.get('validation_rules', {})
    transformed = []
    invalid_count = 0
    
    for item in items:
        is_valid, errors = validate_item(item, validation_rules)
        
        if is_valid:
            # Transformation durchführen
            if 'email' in item:
                item['email'] = item['email'].lower().strip()
            
            if 'name' in item:
                item['name'] = item['name'].strip()
            
            transformed.append(item)
        else:
            log.warning(f"Item {item.get('id', 'unknown')} validation failed: {errors}")
            invalid_count += 1
    
    log.info(f"Transformed {len(transformed)} items, {invalid_count} invalid")
    return transformed
```

---

## Utilities

### Logger

**Speicherort:** `scripts/utils/logger.py`

```python
import logging
import json

def setup_logger(config_path: str = "config/logging.json"):
    """
    Konfiguriert das Logging-System.
    
    Args:
        config_path (str): Pfad zur Logging-Konfiguration
    """
    import logging.config
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    logging.config.dictConfig(config)

# In deinem Code:
from scripts.utils.logger import setup_logger

setup_logger()
log = logging.getLogger(__name__)
log.info("Logger initialized")
```

---

## Eigene Erweiterungen

### Neue Extract-Klasse erstellen

1. **Erstelle neue Datei** in `scripts/classes/ETLExtract/`:

```python
# scripts/classes/ETLExtract/ETLExtractMySource.py

import logging
from scripts.classes.ETLExtract.ETLExtractBase import ETLExtractBase

log = logging.getLogger(__name__)

class ETLExtractMySource(ETLExtractBase):
    """
    Extract-Klasse für meine Datenquelle.
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.my_url = config.get("my_url", "")
        self.my_api_key = config.get("my_api_key", "")
        log.info(f"Initialized ETLExtractMySource with name: {self.name}")
    
    def extract(self) -> dict:
        """
        Extrahiert Daten aus meiner Quelle.
        """
        log.info(f"Extracting data from {self.name}")
        
        # Deine Extraktionslogik hier
        items = []
        # ... Code zum Abrufen der Daten ...
        
        result = {
            "items": items,
            "count": len(items)
        }
        
        # Debug-Daten speichern
        if self.debug:
            self.save_debug_data(result, "data")
        
        return result
```

2. **Registriere die Klasse** in `main.py` oder einer Factory:

```python
# In main.py oder einer Factory-Klasse
from scripts.classes.ETLExtract.ETLExtractMySource import ETLExtractMySource

# Factory-Pattern
def create_extractor(config: dict):
    extract_type = config.get("type", "").lower()
    
    if extract_type == "mysource":
        return ETLExtractMySource(config)
    elif extract_type == "gevisapi":
        return ETLExtractGevisApi(config)
    # ... weitere Typen
    
    raise ValueError(f"Unknown extract type: {extract_type}")
```

3. **Verwende in Konfiguration**:

```python
"extraction": {
    "type": "mysource",
    "name": "My Custom Source",
    "my_url": "https://api.example.com",
    "my_api_key": "secret_key"
}
```

### Neue Load-Klasse erstellen

Analog zur Extract-Klasse, aber mit `load()` Methode statt `extract()`.

---

## Error Handling

### Best Practices

```python
import logging

log = logging.getLogger(__name__)

def safe_operation():
    try:
        # Operation durchführen
        result = perform_operation()
        return True, result
    
    except ConnectionError as e:
        log.error(f"Connection error: {e}")
        return False, None
    
    except ValueError as e:
        log.error(f"Value error: {e}")
        return False, None
    
    except Exception as e:
        log.exception(f"Unexpected error: {e}")
        return False, None
    
    finally:
        # Cleanup
        cleanup_resources()
```

---

## Testing

### Unit-Test-Beispiel

```python
# tests/test_extract_gevisapi.py

import unittest
from unittest.mock import patch, Mock
from scripts.classes.ETLExtract.ETLExtractGevisApi import ETLExtractGevisApi

class TestETLExtractGevisApi(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            "name": "Test Extract",
            "authorization": {
                "client_id": "test_id",
                "client_secret": "test_secret"
            },
            "base_url": "https://api.test.com",
            "endpoint": "/api/test",
            "mapping": {"id": "id"}
        }
    
    @patch('requests.post')
    def test_get_access_token(self, mock_post):
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Test
        extractor = ETLExtractGevisApi(self.config)
        token = extractor.get_access_token()
        
        self.assertEqual(token, "test_token")

if __name__ == '__main__':
    unittest.main()
```

---

## Weitere Ressourcen

- [Konfigurationsanleitung](CONFIGURATION.md)
- [Beispiele](EXAMPLES.md)
- [Installation](INSTALLATION.md)

---

**Hinweis**: Diese API-Referenz wird kontinuierlich erweitert.
