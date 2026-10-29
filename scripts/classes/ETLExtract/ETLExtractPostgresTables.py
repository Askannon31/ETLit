########################################################################################################################
# Class for ETL Extraction of complete tables (structure + data) from a PostgreSQL Database                            #
########################################################################################################################
import logging
import uuid

from scripts.classes.ETLExtract.ETLExtractPostgres import ETLExtractPostgres


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)


########################################################################################################################
# ETLExtractPostgresTables                                                                                             #
########################################################################################################################
class ETLExtractPostgresTables(ETLExtractPostgres):
    """
    Extracts complete PostgreSQL tables including column metadata.
    Rows are streamed in chunks so that large tables do not have to fit into memory.
    """

    def __init__(self, config):
        super().__init__(config)
        self.tables = config.get("tables", []) or []
        self.chunk_size = int(config.get("chunk_size", 10000))
        self.include_primary_key = bool(config.get("include_primary_key", False))
        self.table_definitions: list[dict] = []

    def __str__(self):
        return f"ETLExtractPostgresTables({self.host}:{self.port}, {self.database}, tables={self.tables})"

    def _read_columns(self, schema_name: str, table_name: str) -> list[dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT column_name, data_type, udt_name, character_maximum_length,
                   numeric_precision, numeric_scale, datetime_precision, is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """,
            (schema_name, table_name),
        )
        return [
            {
                "name": row[0],
                "data_type": row[1],
                "udt_name": row[2],
                "character_maximum_length": row[3],
                "numeric_precision": row[4],
                "numeric_scale": row[5],
                "datetime_precision": row[6],
                "nullable": row[7] == "YES",
            }
            for row in cursor.fetchall()
        ]

    def _read_primary_key(self, schema_name: str, table_name: str) -> list[str]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = %s AND tc.table_name = %s
            ORDER BY kcu.ordinal_position
            """,
            (schema_name, table_name),
        )
        return [row[0] for row in cursor.fetchall()]

    def setup(self) -> bool:
        """
        Connect to PostgreSQL and read the structure of all configured tables.
        Returns False if no tables are configured or a table does not exist.
        """
        try:
            if not self.tables:
                log.error("No tables configured for extraction.")
                return False

            self.conn = self.connect()
            self.table_definitions = []

            for table_entry in self.tables:
                if isinstance(table_entry, dict):
                    table_ref = table_entry.get("table", "")
                    where_clause = (table_entry.get("where") or "").strip()
                else:
                    table_ref = table_entry
                    where_clause = ""

                schema_name, table_name = self._resolve_schema_and_table(table_ref)
                columns = self._read_columns(schema_name, table_name)
                if not columns:
                    log.error(f"Table '{schema_name}.{table_name}' does not exist or has no accessible columns.")
                    self.conn.close()
                    return False

                primary_key = self._read_primary_key(schema_name, table_name) if self.include_primary_key else []
                self.table_definitions.append({
                    "source_schema": schema_name,
                    "name": table_name,
                    "columns": columns,
                    "primary_key": primary_key,
                    "where": where_clause,
                })
                filter_info = f", filter: {where_clause}" if where_clause else ""
                log.info(f"Read structure of '{schema_name}.{table_name}' ({len(columns)} columns{filter_info}).")

            # End the read transaction of the metadata queries
            self.conn.rollback()
            return True
        except Exception as e:
            log.error(f"Setup failed: {e}")
            return False

    def _stream_rows(self, table_definition: dict):
        """
        Generator yielding lists of row tuples using a server-side cursor.
        """
        schema_name = table_definition["source_schema"]
        table_name = table_definition["name"]
        column_list = ", ".join(self._quote_identifier(column["name"]) for column in table_definition["columns"])
        query = f"SELECT {column_list} FROM {self._qualified_table_name(schema_name, table_name)}"
        if table_definition.get("where"):
            # Filter is raw SQL from the trusted config file
            query += f" WHERE ({table_definition['where']})"

        cursor = self.conn.cursor(name=f"etlit_{uuid.uuid4().hex}")
        try:
            cursor.execute(query)
            while True:
                rows = cursor.fetchmany(self.chunk_size)
                if not rows:
                    break
                yield rows
        finally:
            try:
                cursor.close()
                self.conn.rollback()
            except Exception as e:
                log.warning(f"Could not close cursor for '{schema_name}.{table_name}': {e}")

    def close(self):
        if self.conn is not None and not self.conn.closed:
            self.conn.close()
            log.info("Closed PostgreSQL connection.")

    def extract(self) -> dict:
        """
        Returns the table definitions with lazy row generators.
        The rows are only read from PostgreSQL while the loader consumes them,
        the loader calls data["close"] when finished.
        """
        tables = [{**table_definition, "rows": self._stream_rows(table_definition)}
                  for table_definition in self.table_definitions]
        log.info(f"Prepared {len(tables)} tables for streaming extraction.")
        return {"items": [], "tables": tables, "close": self.close}
