import os

config: dict = {
    "ETL": {
        "processes": [
            {
                "name": "ExampleETLProcess",
                "description": "An example ETL process configuration",
                "active": False,
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
                        "$filter": "systemModifiedAt gt 2025-10-01T11:47:03.117Z"
                    },
                    "mapping": {
                        "lfdNr": "lfdNr",
                        "id": "id",
                        "documentNo": "no",
                        "documentDate": "date",
                        "dmsNo": "dokuid",
                        "ledgerAccount": "account",
                        "CostAccountCode": "costaccount"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks.py",
                    "function_name": "transform_items",
                    "config": {}
                },
                "loading": {
                    "type": "d3businessobjects",
                    "name": "My D3 Business Objects Source",
                    "base_url": os.environ.get("D3_API_BASE_URL"),
                    "api_key": os.environ.get("D3_API_KEY"),
                    "batch_size": 100,
                    "model": "latescanning",
                    "truncate_before_load": True,
                    "entity": {
                        "name": "ItemLedgerEntry",
                        "plural": "ItemLedgerEntries",
                        "definition": {
                            "name": "ItemLedgerEntry",
                            "pluralName": "ItemLedgerEntries",
                            "description": "ItemLedgerEntries entity type",
                            "state": "published",
                            "key": {
                                "name": "id",
                                "type": "string",
                                "state": "published"
                            },
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
                                    "name": "dmsNo",
                                    "type": "string",
                                    "state": "published"
                                },
                                {
                                    "name": "ledgerAccount",
                                    "type": "string",
                                    "state": "published"
                                },
                                {
                                    "name": "costAccountCode",
                                    "type": "string",
                                    "state": "published"
                                },
                                {
                                    "name": "companyName",
                                    "type": "string",
                                    "state": "published"
                                }
                            ]
                        }
                    },
                    "mapping": {
                        "id": "lfdNr",
                        "id": "id",
                        "no": "no",
                        "date": "documentDate",
                        "dokuid": "dmsNo",
                        "account": "ledgerAccount",
                        "costaccount": "costAccountCode",
                        "company": "companyName"
                    }

                }
            },
            {
                "name": "ExampleETLProcess CSV-File",
                "description": "An example ETL process configuration with CSV file extraction",
                "active": False,
                "extraction": {
                    "type": "csvfile",
                    "file_path": "data/input/data.csv",
                    "save_path": "data/save",
                    "delimiter": ";",
                    "encoding": "utf-8",
                    "columns": [
                        "lfdNr",
                        "id",
                        "no",
                        "date",
                        "dokuid",
                        "account",
                        "costaccount"
                    ],
                    "mapping": {
                        "lfdNr": "lfdNr",
                        "id": "id",
                        "no": "no",
                        "date": "date",
                        "dokuid": "dokuid",
                        "account": "account",
                        "costaccount": "costaccount"
                    },
                    "debug": True
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks.py",
                    "function_name": "transform_items",
                    "config": {}
                },
                "loading": {
                    "type": "mssql",
                    "name": "Insert Data into a MSSQL Database Table",
                    "connection": {
                        "server": "dms-dev",
                        "database": "masterdata",
                        "username": os.environ.get("MSSQL_USERNAME", "your_username"),
                        "password": os.environ.get("MSSQL_PASSWORD", "your_password")
                    },
                    "table": "ETLitTest",
                    "insert_statement": "INSERT INTO ETLitTest (id, lfdNr, no, date, dokuid, account, costaccount, company) VALUES ('@TargetField1', '@TargetField2', '@TargetField3', '@TargetField4', '@TargetField5', '@TargetField6', '@TargetField7', '@TargetField8')",
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
            },
            {
                "name": "ExampleETLProcess CSV-File",
                "description": "An example ETL process configuration with CSV file extraction",
                "active": False,
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
                        "$filter": "systemModifiedAt gt 2025-10-01T11:47:03.117Z"
                    },
                    "mapping": {
                        "lfdNr": "lfdNr",
                        "id": "id",
                        "documentNo": "no",
                        "documentDate": "date",
                        "dmsNo": "dokuid",
                        "ledgerAccount": "account",
                        "CostAccountCode": "costaccount"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks.py",
                    "function_name": "transform_items",
                    "config": {}
                },
                "loading": {
                    "type": "mssql",
                    "name": "Insert Data into a MSSQL Database Table",
                    "connection": {
                        "server": "dms-dev",
                        "database": "masterdata",
                        "username": os.environ.get("MSSQL_USERNAME", "your_username"),
                        "password": os.environ.get("MSSQL_PASSWORD", "your_password")
                    },
                    "table": "ETLitTest",
                    "insert_statement": "INSERT INTO ETLitTest (id, lfdNr, no, date, dokuid, account, costaccount, company) VALUES ('@TargetField1', '@TargetField2', '@TargetField3', '@TargetField4', '@TargetField5', '@TargetField6', '@TargetField7', '@TargetField8')",
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
            },
            {
                "name": "ExampleETLProcess",
                "description": "An example ETL process configuration",
                "active": True,
                "extraction": {
                    "type": "mssql",
                    "name": "Extract Data from a MSSQL Database Table",
                    "connection": {
                        "server": "dms-dev",
                        "database": "masterdata",
                        "username": os.environ.get("MSSQL_USERNAME", "your_username"),
                        "password": os.environ.get("MSSQL_PASSWORD", "your_password")
                    },
                    "table": "ETLitTest",
                    "query": "SELECT [id],[lfdNr],[no],[date],[dokuid],[account],[costaccount],[company] FROM [dbo].[ETLitTest]",
                    "mapping": [
                        {
                            "target_field": "id",
                            "data_type": "string"
                        },
                        {
                            "target_field": "lfdNr",
                            "data_type": "string"
                        },
                        {
                            "target_field": "no",
                            "data_type": "string"
                        },
                        {
                            "target_field": "date",
                            "data_type": "string"
                        },
                        {
                            "target_field": "dokuid",
                            "data_type": "string"
                        },
                        {
                            "target_field": "account",
                            "data_type": "string"
                        },
                        {
                            "target_field": "costaccount",
                            "data_type": "string"
                        },
                        {
                            "target_field": "company",
                            "data_type": "string"
                        }
                    ]
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks.py",
                    "function_name": "transform_items",
                    "config": {}
                },
                "loading": {
                    "type": "d3businessobjects",
                    "name": "My D3 Business Objects Source",
                    "base_url": os.environ.get("D3_API_BASE_URL"),
                    "api_key": os.environ.get("D3_API_KEY"),
                    "batch_size": 100,
                    "model": "latescanning",
                    "truncate_before_load": True,
                    "entity": {
                        "name": "ItemLedgerEntry",
                        "plural": "ItemLedgerEntries",
                        "definition": {
                            "name": "ItemLedgerEntry",
                            "pluralName": "ItemLedgerEntries",
                            "description": "ItemLedgerEntries entity type",
                            "state": "published",
                            "key": {
                                "name": "id",
                                "type": "string",
                                "state": "published"
                            },
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
                                    "name": "dmsNo",
                                    "type": "string",
                                    "state": "published"
                                },
                                {
                                    "name": "ledgerAccount",
                                    "type": "string",
                                    "state": "published"
                                },
                                {
                                    "name": "costAccountCode",
                                    "type": "string",
                                    "state": "published"
                                },
                                {
                                    "name": "companyName",
                                    "type": "string",
                                    "state": "published"
                                }
                            ]
                        }
                    },
                    "mapping": {
                        "id": "lfdNr",
                        "id": "id",
                        "no": "no",
                        "date": "documentDate",
                        "dokuid": "dmsNo",
                        "account": "ledgerAccount",
                        "costaccount": "costAccountCode",
                        "company": "companyName"
                    }

                }
            }
        ]
    }
}