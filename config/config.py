import os

config: dict = {
    "ETL": {
        "processes": [
            {
                "name": "Get sscan Master Data Vendor",
                "description": "Get sscan Master Data Vendor from DB",
                "active": False,
                "extraction": {
                    "type": "postgres",
                    "name": "PostgreSQL Quelle",

                    # Verbindungsdaten
                    "connection": {
                        "host": os.environ.get("POSTGRES_HOST"),
                        "port": 5432,
                        "database": os.environ.get("POSTGRES_DATABASE"),
                        "username": os.environ.get("POSTGRES_USERNAME"),
                        "password": os.environ.get("POSTGRES_PASSWORD"),
                        "sslmode": "prefer",          # Optional
                        "connect_timeout": 30           # Optional
                    },
                    "query": "SELECT ven.[displayName] AS 'Name1', '' AS 'Name2', ven.[country] AS 'COUNTRYCODE', ven.[postalCode] AS 'ZIP', ven.[city] AS 'CITY', '' AS 'BANKCOUNTRY', '' AS 'BANKSORTCODE', vb.BankAccountNo AS 'BANKACCOUNT', ven.taxRegistrationNumber AS 'VATREGNO', 'Integrationstest' AS 'COMPANYCODE', vb.iban AS 'IBAN', '' AS 'NATIONALTAX', '' AS 'XPRO1', '' AS 'XPRO2', pt.code AS 'XPRO3', '' AS 'XPRO4', '' AS 'XPRO5', ven.[number] AS 'CREDITORID', '' AS 'ADDRESS', '' AS 'EMAIL', '' AS 'COMMENT', '' AS 'STATE', '' AS 'STREET' FROM [MasterData].[dbo].[VeoVendors] AS ven LEFT JOIN [MasterData].[dbo].[VeoVendorBank] as vb ON ven.number = vb.vendorNo LEFT JOIN [masterdata].[dbo].[VeoPaymentTerms] AS pt ON pt.id = ven.[paymentTermsId]",
                    "mapping": [
                        {
                            "target_field": "NAME1",
                            "data_type": "string"
                        },
                        {
                            "target_field": "NAME2",
                            "data_type": "string"
                        },
                        {
                            "target_field": "COUNTRYCODE",
                            "data_type": "string"
                        },
                        {
                            "target_field": "ZIP",
                            "data_type": "string"
                        },
                        {
                            "target_field": "CITY",
                            "data_type": "string"
                        },
                        {
                            "target_field": "BANKCOUNTRY",
                            "data_type": "string"
                        },
                        {
                            "target_field": "BANKSORTCODE",
                            "data_type": "string"
                        },
                        {
                            "target_field": "BANKACCOUNT",
                            "data_type": "string"
                        },
                        {
                            "target_field": "VATREGNO",
                            "data_type": "string"
                        },
                        {
                            "target_field": "COMPANYCODE",
                            "data_type": "string"
                        },
                        {
                            "target_field": "IBAN",
                            "data_type": "string"
                        },
                        {
                            "target_field": "NATIONALTAX",
                            "data_type": "string"
                        },
                        {
                            "target_field": "XPRO1",
                            "data_type": "string"
                        },
                        {
                            "target_field": "XPRO2",
                            "data_type": "string"
                        },
                        {
                            "target_field": "XPRO3",
                            "data_type": "string"
                        },
                        {
                            "target_field": "XPRO4",
                            "data_type": "string"
                        },
                        {
                            "target_field": "XPRO5",
                            "data_type": "string"
                        },
                        {
                            "target_field": "CREDITORID",
                            "data_type": "string"
                        },
                        {
                            "target_field": "ADDRESS",
                            "data_type": "string"
                        },
                        {
                            "target_field": "EMAIL",
                            "data_type": "string"
                        },
                        {
                            "target_field": "COMMENT",
                            "data_type": "string"
                        },
                        {
                            "target_field": "STATE",
                            "data_type": "string"
                        },
                        {
                            "target_field": "STREET",
                            "data_type": "string"
                        }
                    ]
                },
                "transformation": {},
                "loading": {
                    "type": "csv",
                    "name": "Export to CSV File",
                    "path": "data/output",
                    "filename": "Master_Creditor.csv",
                    "delimiter": ";",
                    "header": True,
                    "overwrite": True,
                    "mappings": {
                        "Name1": "Name1",
                        "Name2": "Name2",
                        "COUNTRYCODE": "COUNTRYCODE",
                        "ZIP": "ZIP",
                        "CITY": "CITY",
                        "BANKCCOUNTRY": "BANKCOUNTRY",
                        "BANKSORTCODE": "BANKSORTCODE",
                        "BANKACCOUNT": "BANKACCOUNT",
                        "VATREGNO": "VATREGNO",
                        "COMPANYCODE": "COMPANYCODE",
                        "IBAN": "IBAN",
                        "NATIONALTAX": "NATIONALTAX",
                        "XPRO1": "XPRO1",
                        "XPRO2": "XPRO2",
                        "XPRO3": "XPRO3",
                        "XPRO4": "XPRO4",
                        "XPRO5": "XPRO5",
                        "CREDITORID": "CREDITORID",
                        "ADDRESS": "ADDRESS",
                        "EMAIL": "EMAIL",
                        "COMMENT": "COMMENT",
                        "STATE": "STATE",
                        "STREET": "STREET"
                    }
                }
            },
            {
                "name": "Copy Postgres Tables to MSSQL",
                "description": "Copy complete tables (structure + data) from PostgreSQL to MSSQL",
                "active": False,
                "extraction": {
                    "type": "postgres_tables",
                    "name": "PostgreSQL Tabellen",
                    "connection": {
                        "host": os.environ.get("POSTGRES_HOST"),
                        "port": 5432,
                        "database": os.environ.get("POSTGRES_DATABASE"),
                        "username": os.environ.get("POSTGRES_USERNAME"),
                        "password": os.environ.get("POSTGRES_PASSWORD"),
                        "sslmode": "prefer",
                        "connect_timeout": 30
                    },
                    "schema": "public",
                    "tables": [
                        "your_table",
                        # {"table": "your_schema.your_table", "where": "created_at >= '2024-01-01'"},
                    ],
                    "chunk_size": 10000,
                    "include_primary_key": True
                },
                "transformation": {},
                "loading": {
                    "type": "mssql_tables",
                    "name": "MSSQL Tabellen",
                    "connection": {
                        "server": os.environ.get("MSSQL_SERVER"),
                        "database": os.environ.get("MSSQL_DATABASE"),
                        "username": os.environ.get("MSSQL_USERNAME"),
                        "password": os.environ.get("MSSQL_PASSWORD"),
                        "driver": "{ODBC Driver 17 for SQL Server}"
                    },
                    "target_schema": "dbo",
                    "create_primary_key": True,
                    "fast_executemany": True
                }
            },
        ]
    }
}