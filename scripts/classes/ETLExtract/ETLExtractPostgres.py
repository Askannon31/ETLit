########################################################################################################################
# Class for ETL Extraction from a PostgreSQL Database table                                                            #
########################################################################################################################
import logging
import psycopg

from scripts.classes.ETLExtract.ETLExtractBase import ETLExtractBase


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)


########################################################################################################################
# ETLExtractPostgres                                                                                                   #
########################################################################################################################
class ETLExtractPostgres(ETLExtractBase):
    def __init__(self, config):
        super().__init__(config)
        connection_config = config.get("connection", {}) or {}

        self.host = connection_config.get("host", connection_config.get("server", "localhost"))
        self.port = int(connection_config.get("port", 5432))
        self.database = connection_config.get("database", connection_config.get("dbname", "postgres"))
        self.username = connection_config.get("username", connection_config.get("user", "postgres"))
        self.password = connection_config.get("password", "")
        self.sslmode = connection_config.get("sslmode")
        self.connect_timeout = int(connection_config.get("connect_timeout", 10))
        self.mapping = config.get("mappings", config.get("mapping", {}))
        self.conn = None

    def __str__(self):
        return f"ETLExtractPostgres({self.host}:{self.port}, {self.database})"

    def _resolve_schema_and_table(self, table_name: str) -> tuple[str, str]:
        schema_name = self.config.get("schema", "public")
        resolved_table = table_name

        if "." in table_name:
            schema_part, table_part = table_name.split(".", 1)
            schema_name = schema_part.strip() or schema_name
            resolved_table = table_part.strip()

        return schema_name, resolved_table

    def _quote_identifier(self, identifier: str) -> str:
        return '"' + identifier.replace('"', '""') + '"'

    def _qualified_table_name(self, schema_name: str, table_name: str) -> str:
        return f"{self._quote_identifier(schema_name)}.{self._quote_identifier(table_name)}"

    def connect(self):
        """
        Establish a connection to the PostgreSQL database.

        :return: psycopg Connection object
        """
        try:
            connect_kwargs = {
                "host": self.host,
                "port": self.port,
                "dbname": self.database,
                "user": self.username,
                "password": self.password,
                "connect_timeout": self.connect_timeout,
            }
            if self.sslmode:
                connect_kwargs["sslmode"] = self.sslmode

            connection = psycopg.connect(**connect_kwargs)
            log.info("Successfully connected to PostgreSQL database.")
            return connection
        except Exception as e:
            log.error(f"Error connecting to PostgreSQL database: {e}")
            raise

    def setup(self) -> bool:
        """
        Setup the PostgreSQL database connection and verify connectivity.
        Check if the source table exists when table is configured.
        """
        try:
            self.conn = self.connect()
            configured_query = self.config.get("query")
            table_name = self.config.get("table")

            if configured_query or not table_name:
                return True

            schema_name, resolved_table = self._resolve_schema_and_table(table_name)
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
                """,
                (schema_name, resolved_table),
            )

            if cursor.fetchone():
                log.info(f"Table '{schema_name}.{resolved_table}' exists in the database.")
                return True

            log.warning(f"Table '{schema_name}.{resolved_table}' does not exist in the database.")
            return False
        except Exception as e:
            log.error(f"Setup failed: {e}")
            return False

    def extract(self) -> dict:
        """
        Extract data from the PostgreSQL database table based on the provided SQL query.
        Returns extracted rows as a {"items": [...]} dictionary.
        """
        try:
            cursor = self.conn.cursor()
            query = self.config.get("query")

            if not query:
                table_name = self.config.get("table", "source_table")
                schema_name, resolved_table = self._resolve_schema_and_table(table_name)
                query = f"SELECT * FROM {self._qualified_table_name(schema_name, resolved_table)}"

            cursor.execute(query)
            columns = [column.name for column in cursor.description]
            rows = cursor.fetchall()
            data = {"items": [dict(zip(columns, row)) for row in rows]}
            log.info(f"Extracted {len(data['items'])} records from PostgreSQL database.")
            return data
        except Exception as e:
            log.error(f"Data extraction failed: {e}")
            return {"items": []}
