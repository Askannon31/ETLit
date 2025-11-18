import os

config: dict = {
    "ETL": {
        "processes": [
            {
                "name": "ExampleETLProcess",
                "description": "An example ETL process configuration",
                "extraction": {
                    "type": "gevisapi",
                    "name": "Delbrueck Item Ledger Entries",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/api/gws/ecm/v1.0/itemLedgerEntries",
                    "query_parameters": {
                        "company": "Raiff. Delbrück",
                        "$filter": "dmsNo eq '00109437'"
                    },
                    "mapping": {
                        "lfdNr": 0,
                        "id": "id",
                        "documentNo": "no",
                        "documentDate": "date",
                        "dmsNo": "dokuid",
                        "ledgerAccount": "account",
                        "CostAccountCode": "costaccount"
                    }
                },
                "transformation": {},
                "destination": {}
            }
        ]
    }
}