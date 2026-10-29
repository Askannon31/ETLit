########################################################################################################################
# Class to Load complete tables into a MSSQL Database (drop + create + insert)                                         #
########################################################################################################################
import datetime
import decimal
import json
import logging
import re

import pyodbc

from scripts.classes.ETLLoad.ETLLoadMSSQL import ETLLoadMSSQL


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)

NVARCHAR_MAX_LENGTH = 4000
DECIMAL_MAX_PRECISION = 38
DECIMAL_CONTEXT = decimal.Context(prec=DECIMAL_MAX_PRECISION)
DECIMAL_TYPE_PATTERN = re.compile(r"^DECIMAL\((\d+),(\d+)\)$")


########################################################################################################################
#                                                  Value converters                                                    #
########################################################################################################################
def _to_text(value):
    if value is None or isinstance(value, str):
        return value
    return str(value)


def _to_json(value):
    if value is None or isinstance(value, str):
        return value
    return json.dumps(value, default=str)


def _to_iso(value):
    # pyodbc cannot bind timezone-aware values, SQL Server converts ISO 8601 strings implicitly
    if value is None or isinstance(value, str):
        return value
    return value.isoformat()


def _to_uuid_text(value):
    return None if value is None else str(value)


def _decimal_converter(scale: int):
    exponent = decimal.Decimal(1).scaleb(-scale)

    def convert(value):
        if value is None:
            return None
        if not isinstance(value, decimal.Decimal):
            value = decimal.Decimal(str(value))
        # SQL Server has no NaN/Infinity for DECIMAL
        if not value.is_finite():
            return None
        return value.quantize(exponent, rounding=decimal.ROUND_HALF_UP, context=DECIMAL_CONTEXT)

    return convert


########################################################################################################################
# ETLLoadMSSQLTables                                                                                                   #
########################################################################################################################
class ETLLoadMSSQLTables(ETLLoadMSSQL):
    """
    Loads complete tables (as provided by ETLExtractPostgresTables) into MSSQL.
    Existing target tables are dropped and recreated.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.target_schema = config.get("target_schema", "dbo")
        self.create_primary_key = bool(config.get("create_primary_key", False))
        self.fast_executemany = bool(config.get("fast_executemany", True))

    def __str__(self):
        return f"ETLLoadMSSQLTables({self.server}, {self.database}, schema={self.target_schema})"

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        return "[" + identifier.replace("]", "]]") + "]"

    def _qualified_table_name(self, table_name: str) -> str:
        return f"{self._quote_identifier(self.target_schema)}.{self._quote_identifier(table_name)}"

    @staticmethod
    def _map_column_type(column: dict) -> tuple[str, object]:
        """
        Maps a PostgreSQL column definition to a MSSQL type and an optional value converter.
        """
        data_type = (column.get("data_type") or "").lower()
        length = column.get("character_maximum_length")
        precision = column.get("numeric_precision")
        scale = column.get("numeric_scale")
        datetime_precision = column.get("datetime_precision")
        fraction = 6 if datetime_precision is None else min(int(datetime_precision), 7)

        if data_type == "smallint":
            return "SMALLINT", None
        if data_type == "integer":
            return "INT", None
        if data_type == "bigint":
            return "BIGINT", None
        if data_type == "numeric":
            if precision is None:
                return "DECIMAL(38,10)", _decimal_converter(10)
            precision = min(int(precision), DECIMAL_MAX_PRECISION)
            scale = min(int(scale or 0), precision)
            return f"DECIMAL({precision},{scale})", _decimal_converter(scale)
        if data_type == "real":
            return "REAL", None
        if data_type == "double precision":
            return "FLOAT", None
        if data_type == "boolean":
            return "BIT", None
        if data_type == "character varying":
            if length is None or int(length) > NVARCHAR_MAX_LENGTH:
                return "NVARCHAR(MAX)", None
            return f"NVARCHAR({int(length)})", None
        if data_type == "character":
            if length is None:
                return "NCHAR(1)", None
            if int(length) > NVARCHAR_MAX_LENGTH:
                return "NVARCHAR(MAX)", None
            return f"NCHAR({int(length)})", None
        if data_type == "text":
            return "NVARCHAR(MAX)", None
        if data_type == "date":
            return "DATE", None
        if data_type == "time without time zone":
            return f"TIME({fraction})", None
        if data_type == "time with time zone":
            return "NVARCHAR(50)", _to_iso
        if data_type == "timestamp without time zone":
            return f"DATETIME2({fraction})", None
        if data_type == "timestamp with time zone":
            return f"DATETIMEOFFSET({fraction})", _to_iso
        if data_type == "uuid":
            return "UNIQUEIDENTIFIER", _to_uuid_text
        if data_type == "bytea":
            return "VARBINARY(MAX)", None
        if data_type in ("json", "jsonb", "array"):
            return "NVARCHAR(MAX)", _to_json
        if data_type in ("interval", "money", "inet", "cidr", "macaddr"):
            return "NVARCHAR(100)", _to_text
        return "NVARCHAR(MAX)", _to_text

    def setup(self) -> bool:
        """
        Connect to MSSQL and make sure the target schema exists.
        """
        try:
            self.conn = self.connect()
            cursor = self.conn.cursor()
            cursor.execute(
                """
                DECLARE @schema SYSNAME = ?;
                IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = @schema)
                BEGIN
                    DECLARE @sql NVARCHAR(MAX) = N'CREATE SCHEMA ' + QUOTENAME(@schema);
                    EXEC (@sql);
                END
                """,
                self.target_schema,
            )
            self.conn.commit()
            log.info(f"Target schema '{self.target_schema}' is available.")
            return True
        except Exception as e:
            log.error(f"Setup failed: {e}")
            return False

    def _recreate_table(self, cursor, table: dict, column_types: list[str]):
        table_name = table["name"]
        qualified_name = self._qualified_table_name(table_name)

        column_definitions = [
            f"{self._quote_identifier(column['name'])} {sql_type} {'NULL' if column.get('nullable', True) else 'NOT NULL'}"
            for column, sql_type in zip(table["columns"], column_types)
        ]

        primary_key = table.get("primary_key") or []
        if self.create_primary_key and primary_key:
            types_by_name = {column["name"]: sql_type for column, sql_type in zip(table["columns"], column_types)}
            if any("(MAX)" in types_by_name.get(column_name, "") for column_name in primary_key):
                log.warning(f"Primary key of '{table_name}' contains a (MAX) column and is not created.")
            else:
                constraint_name = self._quote_identifier(f"PK_{self.target_schema}_{table_name}")
                key_columns = ", ".join(self._quote_identifier(column_name) for column_name in primary_key)
                column_definitions.append(f"CONSTRAINT {constraint_name} PRIMARY KEY ({key_columns})")

        cursor.execute(f"IF OBJECT_ID(?, 'U') IS NOT NULL DROP TABLE {qualified_name}", qualified_name)
        cursor.execute(f"CREATE TABLE {qualified_name} (\n    " + ",\n    ".join(column_definitions) + "\n)")
        self.conn.commit()
        log.info(f"Created table {qualified_name}.")

    def _load_table(self, table: dict) -> bool:
        table_name = table["name"]
        qualified_name = self._qualified_table_name(table_name)
        rows = table["rows"]
        cursor = self.conn.cursor()
        try:
            mapped = [self._map_column_type(column) for column in table["columns"]]
            column_types = [sql_type for sql_type, _ in mapped]
            converters = [(index, converter) for index, (_, converter) in enumerate(mapped) if converter is not None]

            self._recreate_table(cursor, table, column_types)

            column_list = ", ".join(self._quote_identifier(column["name"]) for column in table["columns"])
            placeholders = ", ".join("?" for _ in table["columns"])
            insert_statement = f"INSERT INTO {qualified_name} ({column_list}) VALUES ({placeholders})"
            cursor.fast_executemany = self.fast_executemany

            # Otherwise fast_executemany derives decimal precision from the first row only
            input_sizes = []
            for sql_type in column_types:
                match = DECIMAL_TYPE_PATTERN.match(sql_type)
                input_sizes.append((pyodbc.SQL_DECIMAL, int(match[1]), int(match[2])) if match else None)
            if any(input_sizes):
                cursor.setinputsizes(input_sizes)

            total_rows = 0
            start_time = datetime.datetime.now()
            for chunk in rows:
                if converters:
                    converted_chunk = []
                    for row in chunk:
                        values = list(row)
                        for index, converter in converters:
                            values[index] = converter(values[index])
                        converted_chunk.append(values)
                    chunk = converted_chunk

                cursor.executemany(insert_statement, chunk)
                self.conn.commit()
                total_rows += len(chunk)
                log.info(f"{qualified_name}: {total_rows} rows loaded.")

            duration = (datetime.datetime.now() - start_time).total_seconds()
            log.info(f"Finished {qualified_name}: {total_rows} rows in {duration:.2f} seconds.")
            return True
        except Exception as e:
            self.conn.rollback()
            log.error(f"Load of table {qualified_name} failed: {e}")
            return False
        finally:
            rows.close()
            cursor.close()

    def load(self, data: dict) -> bool:
        """
        Drop, create and fill every table contained in data["tables"].
        """
        tables = data.get("tables", [])
        failed_tables = []
        try:
            for table in tables:
                if not self._load_table(table):
                    failed_tables.append(table["name"])
        finally:
            close_source = data.get("close")
            if callable(close_source):
                close_source()
            self.conn.close()

        if failed_tables:
            log.error(f"{len(failed_tables)} of {len(tables)} tables failed: {', '.join(failed_tables)}")
            return False
        log.info(f"All {len(tables)} tables loaded successfully.")
        return True
