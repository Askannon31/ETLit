########################################################################################################################
# Class to Load data into a MSSQL Database Table.                                                              #
########################################################################################################################
import logging

import pyodbc

from scripts.classes.ETLLoad.ETLLoadBase import ETLLoadBase


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)

class ETLLoadMSSQL(ETLLoadBase):
    """
    Class to Load data into a MSSQL Database Table.
    Inherits from ETLLoadBase.
    """

    def __init__(self, config: dict):
        """
        Initialize the ETLLoadMSSQL class with configuration parameters.

        :param config: Configuration dictionary containing connection parameters.
        """
        super().__init__(config)
        self.server = config.get('connection').get('server', 'localhost')
        self.database = config.get('connection').get('database', 'master')
        self.username = config.get('connection').get('username', 'sa')
        self.password = config.get('connection').get('password', '')
        self.driver = config.get('connection').get('driver', '{ODBC Driver 17 for SQL Server}')
        self.connection_string = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        self.mapping = config.get('mappings', {})
        self.conn = None

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
        Check if the target table exists.
        """
        try:
            self.conn = self.connect()
            cursor = self.conn.cursor()
            table_name = self.config.get('table', 'target_table')
            cursor.execute(f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
            if cursor.fetchone():
                log.info(f"Table '{table_name}' exists in the database.")
            else:
                log.warning(f"Table '{table_name}' does not exist in the database.")
            return True
        except Exception as e:
            log.error(f"Setup failed: {e}")
            return False


    def load(self, data: dict) -> bool:
        """
        Load data into the MSSQL database table.
        """
        try:
            cursor = self.conn.cursor()
            insert_statement = self.config.get('insert_statement', '')
            # for each entry (dict) in data['items'], format and execute the insert statement
            for item in data.get('items', []):
                formatted_statement = insert_statement
                for key, value in item.items():
                    mapping_field = self.mapping.get(key, key)
                    formatted_statement = formatted_statement.replace(f"@{mapping_field}", f"{value}")
                log.debug(f"Formatted insert statement: {formatted_statement}")
                cursor.execute(formatted_statement)
            self.conn.commit()
            log.info("Data loaded successfully.")
            return True
        except Exception as e:
            log.error(f"Load failed: {e}")
            return False