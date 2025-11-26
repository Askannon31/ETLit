import os

config: dict = {
    "ETL": {
        "processes": [
            {
                "name": "Get PaymentTerms",
                "description": "Get PamyentTerms from BC API",
                "active": False,
                "extraction": {
                    "type": "gevisapi",
                    "name": "Leder Brinkmann Payment Terms",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/Production/api/v2.0/paymentTerms",
                    "query_parameters": {
                        "company": "04c410a9-9884-f011-b4ca-002248e4b06e",
                    },
                    "mapping": {
                        "id": "id",
                        "code": "code",
                        "displayName": "displayName",
                        "dueDateCalculation": "dueDateCalculation",
                        "discountDateCalculation": "discountDateCalculation",
                        "discountPercent": "discountPercent",
                        "calculateDiscountOnCreditMemos": "calculateDiscountOnCreditMemos"
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
                    "table": "VeoPaymentTerms ",
                    "insert_statement": "INSERT INTO VeoPaymentTerms  (id, code, displayName, dueDateCalculation, discountDateCalculation, discountPercent, calculateDiscountOnCreditMemos) VALUES ('@TargetField1', '@TargetField2', '@TargetField3', '@TargetField4', '@TargetField5', '@TargetField6', '@TargetField7')",
                    "mappings": {
                        "id": "TargetField1",
                        "code": "TargetField2",
                        "displayName": "TargetField3",
                        "dueDateCalculation": "TargetField4",
                        "discountDateCalculation": "TargetField5",
                        "discountPercent": "TargetField6",
                        "calculateDiscountOnCreditMemos": "TargetField7"
                    }
                }
            },
            {
                "name": "Get Vendors",
                "description": "Get Vendor Data from BC API",
                "active": False,
                "extraction": {
                    "type": "gevisapi",
                    "name": "Leder Brinkmann Vendors",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/Production/api/v2.0/vendors",
                    "query_parameters": {
                        "company": "04c410a9-9884-f011-b4ca-002248e4b06e",
                    },
                    "mapping": {
                        "id": "id",
                        "number": "number",
                        "displayName": "displayName",
                        "addressLine1": "addressLine1",
                        "addressLine2": "addressLine2",
                        "city": "city",
                        "state": "state",
                        "country": "country",
                        "postalCode": "postalCode",
                        "phoneNumber": "phoneNumber",
                        "email": "email",
                        "website": "website",
                        "taxRegistrationNumber": "taxRegistrationNumber",
                        "currencyId": "currencyId",
                        "currencyCode": "currencyCode",
                        "irs1099Code": "irs1099Code",
                        "paymentTermsId": "paymentTermsId",
                        "paymentMethodId": "paymentMethodId",
                        "taxLiable": "taxLiable",
                        "blocked": "blocked",
                        "balance": "balance",
                        "lastModifiedDateTime": "lastModifiedDateTime"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks_LB.py",
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
                    "table": "VeoVendors ",
                    "insert_statement": "INSERT INTO VeoVendors  (id, number, displayName, addressLine1, addressLine2, city, state, country, postalCode, phoneNumber, email, website, taxRegistrationNumber, currencyId, currencyCode, irs1099Code, paymentTermsId, paymentMethodId, taxLiable, blocked, balance, lastModifiedDateTime) VALUES ('@TargetField1@', '@TargetField2@', '@TargetField4@', '@TargetField5@', '@TargetField6@', '@TargetField7@', '@TargetField8@', '@TargetField9@', '@TargetField10@', '@TargetField11@', '@TargetField12@', '@TargetField13@', '@TargetField14@', '@TargetField15@', '@TargetField16@', '@TargetField17@', '@TargetField18@', '@TargetField19@', '@TargetField20@', '@TargetField21@', '@TargetField22@', '@TargetField23@')",
                    "mappings": {
                        "id": "TargetField1",
                        "number": "TargetField2",
                        "displayName": "TargetField4",
                        "addressLine1": "TargetField5",
                        "addressLine2": "TargetField6",
                        "city": "TargetField7",
                        "state": "TargetField8",
                        "country": "TargetField9",
                        "postalCode": "TargetField10",
                        "phoneNumber": "TargetField11",
                        "email": "TargetField12",
                        "website": "TargetField13",
                        "taxRegistrationNumber": "TargetField14",
                        "currencyId": "TargetField15",
                        "currencyCode": "TargetField16",
                        "irs1099Code": "TargetField17",
                        "paymentTermsId": "TargetField18",
                        "paymentMethodId": "TargetField19",
                        "taxLiable": "TargetField20",
                        "blocked": "TargetField21",
                        "balance": "TargetField22",
                        "lastModifiedDateTime": "TargetField23"
                    }
                }
            },
            {
                "name": "Get Vendor Bank",
                "description": "Get Vendor Bank data from gevisECM Extension API",
                "active": False,
                "extraction": {
                    "type": "gevisapi",
                    "name": "Leder Brinkmann Vendor Bank data",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/Production/api/gws/ecm/v1.0/companies(04c410a9-9884-f011-b4ca-002248e4b06e)/vendorBankAccounts",
                    "query_parameters": {
                    },
                    "mapping": {
                        "vendorNo": "vendorNo",
                        "code": "code",
                        "id": "id",
                        "bankBranchNo": "bankBranchNo",
                        "bankAccountNo": "bankAccountNo",
                        "iban": "iban",
                        "systemModifiedAt": "systemModifiedAt",
                        "systemCreatedAt": "systemCreatedAt"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks_LB.py",
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
                    "table": "VeoVendorBank",
                    "insert_statement": "INSERT INTO VeoVendorBank  (vendorNo, code, id, bankBranchNo, bankAccountNo, iban, systemModifiedAt, systemCreatedAt) VALUES ('@vendorNo@', '@code@', '@id@', '@bankBranchNo@', '@bankAccountNo@', '@iban@', '@systemModifiedAt@', '@systemCreatedAt@')",
                    "mappings": {
                        "vendorNo": "vendorNo",
                        "code": "code",
                        "id": "id",
                        "bankBranchNo": "bankBranchNo",
                        "bankAccountNo": "bankAccountNo",
                        "iban": "iban",
                        "systemModifiedAt": "systemModifiedAt",
                        "systemCreatedAt": "systemCreatedAt"
                    }
                }
            },
            {
                "name": "Get GLEntries",
                "description": "Get generalLedgerEntries from BC API",
                "active": False,
                "extraction": {
                    "type": "gevisapi",
                    "name": "Leder Brinkmann GLEntries data",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/Production/api/v2.0/generalLedgerEntries",
                    "query_parameters": {
                        "company": "04c410a9-9884-f011-b4ca-002248e4b06e",
                    },
                    "mapping": {
                        "id": "id",
                        "entryNumber": "entryNumber",
                        "postingDate": "postingDate",
                        "documentNumber": "documentNumber",
                        "documentType": "documentType",
                        "accountId": "accountId",
                        "accountNumber": "accountNumber",
                        "description": "description",
                        "debitAmount": "debitAmount",
                        "creditAmount": "creditAmount",
                        "additionalCurrencyDebitAmount": "additionalCurrencyDebitAmount",
                        "additionalCurrencyCreditAmount": "additionalCurrencyCreditAmount",
                        "lastModifiedDateTime": "lastModifiedDateTime"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks_GLEntries.py",
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
                    "table": "generalLedgerEntry",
                    "insert_statement": "INSERT INTO generalLedgerEntry  (id,entryNumber,postingDate,documentNumber,documentType,accountId,accountNumber,description,debitAmount,creditAmount,additionalCurrencyDebitAmount,additionalCurrencyCreditAmount,lastModifiedDateTime) VALUES ('@id@','@entryNumber@','@postingDate@','@documentNumber@','@documentType@','@accountId@','@accountNumber@','@description@','@debitAmount@','@creditAmount@','@additionalCurrencyDebitAmount@','@additionalCurrencyCreditAmount@','@lastModifiedDateTime@') ",
                    "mappings": {
                        "id": "id",
                        "entryNumber": "entryNumber",
                        "postingDate": "postingDate",
                        "documentNumber": "documentNumber",
                        "documentType": "documentType",
                        "accountId": "accountId",
                        "accountNumber": "accountNumber",
                        "description": "description",
                        "debitAmount": "debitAmount",
                        "creditAmount": "creditAmount",
                        "additionalCurrencyDebitAmount": "additionalCurrencyDebitAmount",
                        "additionalCurrencyCreditAmount": "additionalCurrencyCreditAmount",
                        "lastModifiedDateTime": "lastModifiedDateTime"
                    }
                }
            },
            {
                "name": "Get PostedPurchaseInvoices",
                "description": "Get generalLedgerEntries from gevisECM Extension API",
                "active": False,
                "extraction": {
                    "type": "gevisapi",
                    "name": "Leder Brinkmann GLEntries data",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/Production/api/gws/ecm/v1.0/companies(04c410a9-9884-f011-b4ca-002248e4b06e)/purchaseInvoices",
                    "query_parameters": {
                    },
                    "mapping": {
                        "no": "no",
                        "id": "id",
                        "buyFromVendorNo": "buyFromVendorNo",
                        "buyFromVendorName": "buyFromVendorName",
                        "vendorInvoiceNo": "vendorInvoiceNo",
                        "documentDate": "documentDate",
                        "amountIncludingVat": "amountIncludingVat",
                        "dmsNo": "dmsNo",
                        "dmsNoInvoice": "dmsNoInvoice",
                        "systemModifiedAt": "systemModifiedAt",
                        "systemCreatedAt": "systemCreatedAt"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks_LB.py",
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
                    "table": "PostedPurchaseInvoices",
                    "insert_statement": "INSERT INTO PostedPurchaseInvoices  (no,id,buyFromVendorNo,buyFromVendorName,vendorInvoiceNo,documentDate,amountIncludingVat,dmsNo,dmsNoInvoice,systemModifiedAt,systemCreatedAt) VALUES ('@no@','@id@','@buyFromVendorNo@','@buyFromVendorName@','@vendorInvoiceNo@','@documentDate@','@amountIncludingVat@','@dmsNo@','@dmsNoInvoice@','@systemModifiedAt@','@systemCreatedAt@') ",
                    "mappings": {
                        "no": "no",
                        "id": "id",
                        "buyFromVendorNo": "buyFromVendorNo",
                        "buyFromVendorName": "buyFromVendorName",
                        "vendorInvoiceNo": "vendorInvoiceNo",
                        "documentDate": "documentDate",
                        "amountIncludingVat": "amountIncludingVat",
                        "dmsNo": "dmsNo",
                        "dmsNoInvoice": "dmsNoInvoice",
                        "systemModifiedAt": "systemModifiedAt",
                        "systemCreatedAt": "systemCreatedAt"
                    }
                }
            },
            {
                "name": "Get PostedPurchaseCreditMemos",
                "description": "Get PostedPurchaseCreditMemos from gevisECM Extension API",
                "active": False,
                "extraction": {
                    "type": "gevisapi",
                    "name": "Leder Brinkmann GLEntries data",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/Production/api/gws/ecm/v1.0/companies(04c410a9-9884-f011-b4ca-002248e4b06e)/purchaseCreditMemos",
                    "query_parameters": {
                    },
                    "mapping": {
                        "no": "no",
                        "id": "id",
                        "buyFromVendorNo": "buyFromVendorNo",
                        "buyFromVendorName": "buyFromVendorName",
                        "vendorInvoiceNo": "vendorInvoiceNo",
                        "documentDate": "documentDate",
                        "amountIncludingVat": "amountIncludingVat",
                        "dmsNo": "dmsNo",
                        "dmsNoInvoice": "dmsNoInvoice",
                        "systemModifiedAt": "systemModifiedAt",
                        "systemCreatedAt": "systemCreatedAt"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks_LB.py",
                    "function_name": "transform_items",
                    "config": {}
                },
                "loading": {
                    "type": "mssql",
                    "name": "Insert Data into a MSSQL Database Table",
                    "truncate_before_load": False,
                    "connection": {
                        "server": "dms-dev",
                        "database": "masterdata",
                        "username": os.environ.get("MSSQL_USERNAME", "your_username"),
                        "password": os.environ.get("MSSQL_PASSWORD", "your_password")
                    },
                    "table": "PostedPurchaseInvoices",
                    "insert_statement": "INSERT INTO PostedPurchaseInvoices  (no,id,buyFromVendorNo,buyFromVendorName,vendorInvoiceNo,documentDate,amountIncludingVat,dmsNo,dmsNoInvoice,systemModifiedAt,systemCreatedAt) VALUES ('@no@','@id@','@buyFromVendorNo@','@buyFromVendorName@','@vendorInvoiceNo@','@documentDate@','@amountIncludingVat@','@dmsNo@','@dmsNoInvoice@','@systemModifiedAt@','@systemCreatedAt@') ",
                    "mappings": {
                        "no": "no",
                        "id": "id",
                        "buyFromVendorNo": "buyFromVendorNo",
                        "buyFromVendorName": "buyFromVendorName",
                        "vendorInvoiceNo": "vendorInvoiceNo",
                        "documentDate": "documentDate",
                        "amountIncludingVat": "amountIncludingVat",
                        "dmsNo": "dmsNo",
                        "dmsNoInvoice": "dmsNoInvoice",
                        "systemModifiedAt": "systemModifiedAt",
                        "systemCreatedAt": "systemCreatedAt"
                    }
                }
            },
            {
                "name": "Get Accounts",
                "description": "Get Accounts from gevisECM Extension API",
                "active": True,
                "extraction": {
                    "type": "gevisapi",
                    "name": "Leder Brinkmann Account data",
                    "debug": True,
                    "authorization": {
                        "client_id": os.environ.get("GEVIS_API_CLIENT_ID"),
                        "client_secret": os.environ.get("GEVIS_API_CLIENT_SECRET")
                    },
                    "erp_tenant_id": os.environ.get("GEVIS_API_ERP_TENANT_ID"),
                    "base_url": os.environ.get("GEVIS_API_BASE_URL"),
                    "endpoint": "/Production/api/v2.0/accounts",
                    "query_parameters": {
                        "company": "04c410a9-9884-f011-b4ca-002248e4b06e",
                    },
                    "mapping": {
                        "id": "id",
                        "number": "number",
                        "displayName": "displayName",
                        "category": "category",
                        "subCategory": "subCategory",
                        "blocked": "blocked",
                        "accountType": "accountType",
                        "directPosting": "directPosting",
                        "netChange": "netChange",
                        "consolidationTranslationMethod": "consolidationTranslationMethod",
                        "consolidationDebitAccount": "consolidationDebitAccount",
                        "consolidationCreditAccount": "consolidationCreditAccount",
                        "excludeFromConsolidation": "excludeFromConsolidation",
                        "lastModifiedDateTime": "lastModifiedDateTime"
                    }
                },
                "transformation": {
                    "type": "hookfunction",
                    "name": "transform_hookfunction",
                    "description": "A hook function to transform data items before loading into D3 Business Objects",
                    "debug": True,
                    "hook_file": "scripts/hooks/transform_hooks_LB.py",
                    "function_name": "transform_items",
                    "config": {}
                },
                "loading": {
                    "type": "mssql",
                    "name": "Insert Data into a MSSQL Database Table",
                    "truncate_before_load": False,
                    "connection": {
                        "server": "dms-dev",
                        "database": "masterdata",
                        "username": os.environ.get("MSSQL_USERNAME", "your_username"),
                        "password": os.environ.get("MSSQL_PASSWORD", "your_password")
                    },
                    "table": "VeoAccounts",
                    "insert_statement": "INSERT INTO VeoAccounts (id,number,displayName,category,subCategory,blocked,accountType,directPosting,netChange,consolidationTranslationMethod,consolidationDebitAccount,consolidationCreditAccount,excludeFromConsolidation,lastModifiedDateTime) VALUES ('@id@','@number@','@displayName@','@category@','@subCategory@','@blocked@','@accountType@','@directPosting@','@netChange@','@consolidationTranslationMethod@','@consolidationDebitAccount@','@consolidationCreditAccount@','@excludeFromConsolidation@','@lastModifiedDateTime@')",
                    "mappings": {
                        "id": "id",
                        "number": "number",
                        "displayName": "displayName",
                        "category": "category",
                        "subCategory": "subCategory",
                        "blocked": "blocked",
                        "accountType": "accountType",
                        "directPosting": "directPosting",
                        "netChange": "netChange",
                        "consolidationTranslationMethod": "consolidationTranslationMethod",
                        "consolidationDebitAccount": "consolidationDebitAccount",
                        "consolidationCreditAccount": "consolidationCreditAccount",
                        "excludeFromConsolidation": "excludeFromConsolidation",
                        "lastModifiedDateTime": "lastModifiedDateTime"
                    }
                }
            },
            {
                "name": "Get sscan Master Data Vendor",
                "description": "Get sscan Master Data Vendor from DB",
                "active": False,
                "extraction": {
                    "type": "mssql",
                    "name": "Extract Data from a MSSQL Database Table",
                    "connection": {
                        "server": "dms-dev",
                        "database": "masterdata",
                        "username": os.environ.get("MSSQL_USERNAME", "your_username"),
                        "password": os.environ.get("MSSQL_PASSWORD", "your_password")
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
        ]
    }
}