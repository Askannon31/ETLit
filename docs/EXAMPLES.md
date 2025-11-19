# Beispiele

Diese Seite enthält vollständige Beispiele für verschiedene ETL-Szenarien mit ETLit.

## 📋 Inhaltsverzeichnis

1. [Beispiel 1: CSV zu D3 Business Objects](#beispiel-1-csv-zu-d3-business-objects)
2. [Beispiel 2: Gevis API zu MSSQL](#beispiel-2-gevis-api-zu-mssql)
3. [Beispiel 3: MSSQL zu D3 mit Transformation](#beispiel-3-mssql-zu-d3-mit-transformation)
4. [Beispiel 4: Gevis API zu D3 mit Filter](#beispiel-4-gevis-api-zu-d3-mit-filter)
5. [Beispiel 5: Mehrstufige Transformation](#beispiel-5-mehrstufige-transformation)

---

## Beispiel 1: CSV zu D3 Business Objects

### Szenario
Upload von Produktdaten aus einer CSV-Datei in D3 Business Objects.

### CSV-Datei (`data/input/products.csv`)
```csv
ProductID;ProductName;Price;Category;Stock
P001;Laptop;999.99;Electronics;50
P002;Mouse;29.99;Electronics;200
P003;Desk;299.99;Furniture;30
```

### Konfiguration

```python
{
    "name": "CSV_Products_to_D3",
    "description": "Import product data from CSV to D3",
    "active": True,
    "extraction": {
        "type": "csvfile",
        "name": "Product CSV Extract",
        "debug": True,
        "file_path": "data/input/products.csv",
        "save_path": "data/save",
        "delimiter": ";",
        "encoding": "utf-8",
        "columns": [
            "ProductID",
            "ProductName",
            "Price",
            "Category",
            "Stock"
        ],
        "mapping": {
            "ProductID": "id",
            "ProductName": "name",
            "Price": "price",
            "Category": "category",
            "Stock": "stockQuantity"
        }
    },
    "loading": {
        "type": "d3businessobjects",
        "name": "D3 Products",
        "base_url": os.environ.get("D3_API_BASE_URL"),
        "api_key": os.environ.get("D3_API_KEY"),
        "batch_size": 100,
        "model": "inventory",
        "truncate_before_load": False,
        "entity": {
            "name": "Product",
            "plural": "Products",
            "definition": {
                "name": "Product",
                "pluralName": "Products",
                "description": "Product entity",
                "state": "published",
                "key": {
                    "name": "id",
                    "type": "string",
                    "state": "published"
                },
                "properties": [
                    {
                        "name": "name",
                        "type": "string",
                        "state": "published"
                    },
                    {
                        "name": "price",
                        "type": "decimal",
                        "state": "published"
                    },
                    {
                        "name": "category",
                        "type": "string",
                        "state": "published"
                    },
                    {
                        "name": "stockQuantity",
                        "type": "int32",
                        "state": "published"
                    }
                ]
            }
        },
        "mapping": {
            "id": "id",
            "name": "name",
            "price": "price",
            "category": "category",
            "stockQuantity": "stockQuantity"
        }
    }
}
```

### Ausführung

```bash
python main.py
```

### Erwartetes Ergebnis

```
2025-11-19 10:00:00 - INFO - Starting ETL process: CSV_Products_to_D3
2025-11-19 10:00:00 - INFO - Extracting data from CSV file...
2025-11-19 10:00:01 - INFO - Extracted 3 items
2025-11-19 10:00:01 - INFO - Loading data into D3 Business Objects
2025-11-19 10:00:02 - INFO - Executing batch request with 3 items
2025-11-19 10:00:02 - INFO - Batch request executed successfully
2025-11-19 10:00:02 - INFO - Successfully loaded 3/3 items
```

---

## Beispiel 2: Gevis API zu MSSQL

### Szenario
Abruf von Kundenbestellungen aus der Gevis API und Speicherung in einer MSSQL-Datenbank.

### Datenbank-Schema

```sql
CREATE TABLE CustomerOrders (
    OrderID VARCHAR(50) PRIMARY KEY,
    CustomerName VARCHAR(100),
    OrderDate DATE,
    TotalAmount DECIMAL(10,2),
    Status VARCHAR(20)
);
```

### Konfiguration

```python
{
    "name": "Gevis_Orders_to_MSSQL",
    "description": "Extract orders from Gevis API and load into MSSQL",
    "active": True,
    "extraction": {
        "type": "gevisapi",
        "name": "Gevis Orders Extract",
        "debug": False,
        "authorization": {
            "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
            "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
        },
        "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
        "base_url": os.environ.get("GEVIS_API_BASE_URL"),
        "endpoint": "/api/gws/ecm/v1.0/orders",
        "query_parameters": {
            "company": "My Company",
            "$filter": "orderDate gt 2025-11-01",
            "$orderby": "orderDate desc"
        },
        "mapping": {
            "orderId": "OrderID",
            "customerName": "CustomerName",
            "orderDate": "OrderDate",
            "totalAmount": "TotalAmount",
            "orderStatus": "Status"
        }
    },
    "loading": {
        "type": "mssql",
        "name": "MSSQL Orders Insert",
        "connection": {
            "server": "dms-dev",
            "database": "salesdata",
            "username": os.environ.get("MSSQL_USERNAME"),
            "password": os.environ.get("MSSQL_PASSWORD")
        },
        "table": "CustomerOrders",
        "insert_statement": """
            INSERT INTO CustomerOrders (OrderID, CustomerName, OrderDate, TotalAmount, Status)
            VALUES ('@Field1', '@Field2', '@Field3', '@Field4', '@Field5')
        """,
        "mappings": {
            "OrderID": "Field1",
            "CustomerName": "Field2",
            "OrderDate": "Field3",
            "TotalAmount": "Field4",
            "Status": "Field5"
        }
    }
}
```

---

## Beispiel 3: MSSQL zu D3 mit Transformation

### Szenario
Extrahiere Mitarbeiterdaten aus MSSQL, transformiere sie und lade sie in D3 Business Objects.

### Transformation Hook (`scripts/hooks/employee_transform.py`)

```python
import logging
from datetime import datetime

log = logging.getLogger(__name__)

def transform_employees(items: list, config: dict) -> list:
    """
    Transformiert Mitarbeiterdaten:
    - Formatiert Datumsfelder
    - Berechnet Beschäftigungsdauer
    - Validiert E-Mail-Adressen
    - Bereinigt Telefonnummern
    """
    transformed = []
    
    for item in items:
        try:
            # Datum formatieren
            if 'hire_date' in item:
                hire_date = datetime.strptime(item['hire_date'], '%Y-%m-%d %H:%M:%S')
                item['hire_date'] = hire_date.strftime('%Y-%m-%d')
                
                # Beschäftigungsdauer in Jahren berechnen
                today = datetime.now()
                years = (today - hire_date).days / 365.25
                item['years_employed'] = round(years, 1)
            
            # E-Mail validieren
            if 'email' in item:
                email = item['email'].strip().lower()
                if '@' in email and '.' in email:
                    item['email'] = email
                else:
                    log.warning(f"Invalid email for employee {item.get('id')}: {email}")
                    item['email'] = None
            
            # Telefonnummer bereinigen
            if 'phone' in item:
                phone = ''.join(filter(str.isdigit, item['phone']))
                item['phone'] = phone
            
            # Vollständiger Name
            item['full_name'] = f"{item.get('first_name', '')} {item.get('last_name', '')}".strip()
            
            transformed.append(item)
            
        except Exception as e:
            log.error(f"Error transforming employee {item.get('id')}: {e}")
            continue
    
    log.info(f"Transformed {len(transformed)}/{len(items)} employees")
    return transformed
```

### Konfiguration

```python
{
    "name": "MSSQL_Employees_to_D3",
    "description": "Employee data sync from MSSQL to D3 with transformation",
    "active": True,
    "extraction": {
        "type": "mssql",
        "name": "Employee MSSQL Extract",
        "connection": {
            "server": "hr-server",
            "database": "hrdata",
            "username": os.environ.get("MSSQL_USERNAME"),
            "password": os.environ.get("MSSQL_PASSWORD")
        },
        "query": """
            SELECT 
                emp_id as id,
                first_name,
                last_name,
                email,
                phone,
                hire_date,
                department,
                position
            FROM Employees
            WHERE active = 1
        """,
        "mapping": [
            {"target_field": "id", "data_type": "string"},
            {"target_field": "first_name", "data_type": "string"},
            {"target_field": "last_name", "data_type": "string"},
            {"target_field": "email", "data_type": "string"},
            {"target_field": "phone", "data_type": "string"},
            {"target_field": "hire_date", "data_type": "string"},
            {"target_field": "department", "data_type": "string"},
            {"target_field": "position", "data_type": "string"}
        ]
    },
    "transformation": {
        "type": "hookfunction",
        "name": "Employee Transformation",
        "description": "Transform and enrich employee data",
        "debug": True,
        "hook_file": "scripts/hooks/employee_transform.py",
        "function_name": "transform_employees",
        "config": {
            "date_format": "%Y-%m-%d"
        }
    },
    "loading": {
        "type": "d3businessobjects",
        "name": "D3 Employees",
        "base_url": os.environ.get("D3_API_BASE_URL"),
        "api_key": os.environ.get("D3_API_KEY"),
        "batch_size": 50,
        "model": "hr",
        "entity": {
            "name": "Employee",
            "plural": "Employees",
            "definition": {
                "name": "Employee",
                "pluralName": "Employees",
                "description": "Employee entity",
                "state": "published",
                "key": {
                    "name": "id",
                    "type": "string",
                    "state": "published"
                },
                "properties": [
                    {"name": "full_name", "type": "string", "state": "published"},
                    {"name": "email", "type": "string", "state": "published"},
                    {"name": "phone", "type": "string", "state": "published"},
                    {"name": "hire_date", "type": "date", "state": "published"},
                    {"name": "years_employed", "type": "decimal", "state": "published"},
                    {"name": "department", "type": "string", "state": "published"},
                    {"name": "position", "type": "string", "state": "published"}
                ]
            }
        },
        "mapping": {
            "id": "id",
            "full_name": "full_name",
            "email": "email",
            "phone": "phone",
            "hire_date": "hire_date",
            "years_employed": "years_employed",
            "department": "department",
            "position": "position"
        }
    }
}
```

---

## Beispiel 4: Gevis API zu D3 mit Filter

### Szenario
Inkrementeller Import: Nur Datensätze, die seit dem letzten Lauf geändert wurden.

### Timestamp-Verwaltung (`scripts/utils/timestamp_manager.py`)

```python
import json
import os
from datetime import datetime

class TimestampManager:
    def __init__(self, process_name: str):
        self.process_name = process_name
        self.file_path = f"data/timestamps/{process_name}.json"
        
    def get_last_run(self) -> str:
        """Gibt den Timestamp des letzten Laufs zurück"""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return data.get('last_run', '2020-01-01T00:00:00.000Z')
        return '2020-01-01T00:00:00.000Z'
    
    def update_last_run(self):
        """Aktualisiert den Timestamp"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump({
                'last_run': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'process_name': self.process_name
            }, f, indent=2)
```

### Konfiguration mit dynamischem Filter

```python
from scripts.utils.timestamp_manager import TimestampManager

# Timestamp Manager initialisieren
ts_manager = TimestampManager("ItemLedgerEntries")
last_run = ts_manager.get_last_run()

config = {
    "name": "Gevis_ItemLedger_Incremental",
    "description": "Incremental load of Item Ledger Entries",
    "active": True,
    "extraction": {
        "type": "gevisapi",
        "name": "Gevis Item Ledger Incremental",
        "debug": False,
        "authorization": {
            "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
            "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
        },
        "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
        "base_url": os.environ.get("GEVIS_API_BASE_URL"),
        "endpoint": "/api/gws/ecm/v1.0/itemLedgerEntries",
        "query_parameters": {
            "company": "My Company",
            "$filter": f"systemModifiedAt gt {last_run}",  # Dynamischer Filter!
            "$orderby": "systemModifiedAt asc"
        },
        "mapping": {
            "lfdNr": "id",
            "documentNo": "no",
            "documentDate": "date"
        }
    },
    "loading": {
        "type": "d3businessobjects",
        "name": "D3 Item Ledger",
        "base_url": os.environ.get("D3_API_BASE_URL"),
        "api_key": os.environ.get("D3_API_KEY"),
        "batch_size": 100,
        "model": "latescanning",
        "entity": {
            "name": "ItemLedgerEntry",
            "plural": "ItemLedgerEntries",
            "definition": {
                # ... Definition
            }
        },
        "mapping": {
            "id": "id",
            "no": "no",
            "date": "date"
        }
    }
}

# Nach erfolgreichem Lauf: Timestamp aktualisieren
# ts_manager.update_last_run()
```

---

## Beispiel 5: Mehrstufige Transformation

### Szenario
Komplexe Transformation mit mehreren Schritten: Validierung, Anreicherung, Aggregation.

### Transformation Hooks (`scripts/hooks/complex_transform.py`)

```python
import logging
from typing import Dict, List
import re

log = logging.getLogger(__name__)

def validate_item(item: dict, rules: dict) -> tuple[bool, list]:
    """Validiert ein Item gegen Regeln"""
    errors = []
    
    for field, rule in rules.items():
        if rule == "required" and not item.get(field):
            errors.append(f"Field '{field}' is required")
        elif rule == "email":
            email = item.get(field, '')
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                errors.append(f"Invalid email: {email}")
        elif rule == "numeric":
            value = item.get(field)
            if value and not isinstance(value, (int, float)):
                try:
                    float(value)
                except:
                    errors.append(f"Field '{field}' must be numeric")
    
    return len(errors) == 0, errors


def enrich_item(item: dict, enrichment_data: dict) -> dict:
    """Reichert Item mit zusätzlichen Daten an"""
    # Beispiel: Kundendaten anreichern
    customer_id = item.get('customer_id')
    if customer_id and customer_id in enrichment_data:
        customer = enrichment_data[customer_id]
        item['customer_name'] = customer.get('name')
        item['customer_segment'] = customer.get('segment')
        item['customer_region'] = customer.get('region')
    
    return item


def aggregate_items(items: List[dict], group_by: str) -> List[dict]:
    """Aggregiert Items nach Gruppierungsfeld"""
    aggregated = {}
    
    for item in items:
        key = item.get(group_by)
        if key:
            if key not in aggregated:
                aggregated[key] = {
                    group_by: key,
                    'count': 0,
                    'total_amount': 0,
                    'items': []
                }
            
            aggregated[key]['count'] += 1
            aggregated[key]['total_amount'] += item.get('amount', 0)
            aggregated[key]['items'].append(item)
    
    return list(aggregated.values())


def transform_complex(items: list, config: dict) -> list:
    """
    Komplexe mehrstufige Transformation
    """
    log.info(f"Starting complex transformation for {len(items)} items")
    
    # Schritt 1: Validierung
    validation_rules = config.get('validation_rules', {})
    valid_items = []
    
    for item in items:
        is_valid, errors = validate_item(item, validation_rules)
        if is_valid:
            valid_items.append(item)
        else:
            log.warning(f"Item {item.get('id')} validation failed: {errors}")
    
    log.info(f"Validation: {len(valid_items)}/{len(items)} items valid")
    
    # Schritt 2: Anreicherung
    enrichment_data = config.get('enrichment_data', {})
    enriched_items = []
    
    for item in valid_items:
        enriched = enrich_item(item, enrichment_data)
        enriched_items.append(enriched)
    
    log.info(f"Enrichment: {len(enriched_items)} items enriched")
    
    # Schritt 3: Aggregation (optional)
    if config.get('aggregate'):
        group_by = config.get('aggregate_by', 'customer_id')
        aggregated = aggregate_items(enriched_items, group_by)
        log.info(f"Aggregation: {len(aggregated)} groups created")
        return aggregated
    
    return enriched_items
```

### Konfiguration

```python
{
    "name": "Complex_Transformation_Example",
    "description": "Multi-stage transformation with validation, enrichment, and aggregation",
    "active": True,
    "extraction": {
        "type": "csvfile",
        "file_path": "data/input/orders.csv",
        "delimiter": ",",
        "mapping": {
            "order_id": "id",
            "customer_id": "customer_id",
            "amount": "amount",
            "product_id": "product_id"
        }
    },
    "transformation": {
        "type": "hookfunction",
        "hook_file": "scripts/hooks/complex_transform.py",
        "function_name": "transform_complex",
        "debug": True,
        "config": {
            "validation_rules": {
                "id": "required",
                "customer_id": "required",
                "amount": "numeric"
            },
            "enrichment_data": {
                "C001": {
                    "name": "Acme Corp",
                    "segment": "Enterprise",
                    "region": "North"
                },
                "C002": {
                    "name": "TechStart GmbH",
                    "segment": "SMB",
                    "region": "South"
                }
            },
            "aggregate": True,
            "aggregate_by": "customer_id"
        }
    },
    "loading": {
        "type": "d3businessobjects",
        "name": "D3 Aggregated Orders",
        "base_url": os.environ.get("D3_API_BASE_URL"),
        "api_key": os.environ.get("D3_API_KEY"),
        "batch_size": 100,
        "model": "sales",
        "entity": {
            "name": "CustomerAggregate",
            "plural": "CustomerAggregates",
            "definition": {
                "name": "CustomerAggregate",
                "pluralName": "CustomerAggregates",
                "state": "published",
                "key": {
                    "name": "customer_id",
                    "type": "string",
                    "state": "published"
                },
                "properties": [
                    {"name": "customer_name", "type": "string", "state": "published"},
                    {"name": "customer_segment", "type": "string", "state": "published"},
                    {"name": "customer_region", "type": "string", "state": "published"},
                    {"name": "count", "type": "int32", "state": "published"},
                    {"name": "total_amount", "type": "decimal", "state": "published"}
                ]
            }
        },
        "mapping": {
            "customer_id": "customer_id",
            "customer_name": "customer_name",
            "customer_segment": "customer_segment",
            "customer_region": "customer_region",
            "count": "count",
            "total_amount": "total_amount"
        }
    }
}
```

---

## 🔧 Weitere Beispiele

Weitere Beispiel-Konfigurationen findest du im Verzeichnis `config/examples/`.

## 🆘 Hilfe

Bei Fragen zu den Beispielen:
- Siehe [Konfigurationsanleitung](CONFIGURATION.md)
- Siehe [API-Referenz](API.md)
- Öffne ein Issue auf GitHub

---

**Tipp**: Beginne mit einfachen Beispielen und erweitere sie schrittweise!
