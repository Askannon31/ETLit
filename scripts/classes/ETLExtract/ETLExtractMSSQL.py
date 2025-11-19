########################################################################################################################
# Class for ETL Extraction from a MSSQL Database table                                                                 #
########################################################################################################################
import datetime
import json
import logging
import requests
import pyodbc

from scripts.classes.ETLExtract.ETLExtractBase import ETLExtractBase


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)

########################################################################################################################
# ETLExtractBase                                                                                                       #         
########################################################################################################################
class ETLExtractMSSQL(ETLExtractBase):
    def __init__(self, config):
        super().__init__(config)
        self.server = config.get('connection').get('server', 'localhost')
        self.database = config.get('connection').get('database', 'master')
        self.username = config.get('connection').get('username', 'sa')
        self.password = config.get('connection').get('password', '')
        self.driver = config.get('connection').get('driver', '{ODBC Driver 17 for SQL Server}')
        self.connection_string = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        self.mapping = config.get('mappings', {})
        self.conn = None

    def __str__(self):
        return f"ETLExtractMSSQL({self.server}, {self.database})"

    def connect(self):
        """
        Establish a connection to the MSSQL database.

        :return: pyodbc Connection object
        """
        try:
            connection = pyodbc.connect(self.connection_string)
            log.info("Successfully connected to MSSQL database.")
            return connection
        except pyodbc.Error as e:
            log.error(f"Error connecting to MSSQL database: {e}")
            raise

    
    def setup(self) -> bool:
        """
        Setup the MSSQL database connection and verify connectivity.
        Check if the source table exists.
        """
        try:
            self.conn = self.connect()
            cursor = self.conn.cursor()
            table_name = self.config.get('table', 'source_table')
            cursor.execute(f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
            if cursor.fetchone():
                log.info(f"Table '{table_name}' exists in the database.")
            else:
                log.warning(f"Table '{table_name}' does not exist in the database.")
            return True
        except Exception as e:
            log.error(f"Setup failed: {e}")
            return False

    def extract(self) -> dict:
        """
        Extract data from the MSSQL database table based on the provided SQL query.
        Maps the extracted data rows according to the defined mappings into a {"items": [...]} structure.
        :return: Extracted data as a dictionary.
        """
        try:
            cursor = self.conn.cursor()
            query = self.config.get('query', f"SELECT * FROM {self.config.get('table', 'source_table')}")
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            data = {"items": [dict(zip(columns, row)) for row in rows]}
            log.info(f"Extracted {len(data['items'])} records from MSSQL database.")
            return data
        except Exception as e:
            log.error(f"Data extraction failed: {e}")
            return {"items": []}
