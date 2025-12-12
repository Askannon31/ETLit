########################################################################################################################
# Class to extract data from a csv file.                                                                               #
########################################################################################################################
import logging

import requests

from scripts.classes.ETLExtract.ETLExtractBase import ETLExtractBase


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)
class ETLExtractCSVFile(ETLExtractBase):
    def __init__(self, config):
        super().__init__(config)
        self.name = config.get("name", "ETLExtractCSVFile")
        self.file_path = config.get("file_path", "")
        self.save_path = config.get("save_path", "")
        self.delimiter = config.get("delimiter", ",")
        self.encoding = config.get("encoding", "utf-8")
        self.columns = config.get("columns", [])
        self.mapping = config.get("mapping", {})
        self.debug = config.get("debug", False)

    def __str__(self):
        return f"ETLExtractCSVFile({self.file_path})"

    def setup(self) -> bool:
        # Check if file path ends with *
        # If not, search for the specified file provided in the configuration
        # Else search for any csv file in the directory and use the first one found
        if self.file_path and not self.file_path.lower().endswith(".csv"):
            log.info(f"Searching for specified file: {self.file_path}")
            import os
            if not os.path.isfile(self.file_path):
                log.warning(f"Specified file not found: {self.file_path}")
                
            if self.file_path.endswith("*"):
                log.info(f"Searching for any CSV file in directory: {self.file_path}")
                directory = os.path.dirname(self.file_path)
                file_found = False
                for file in os.listdir(directory):
                    if file.lower().endswith(".csv"):
                        self.file_path = os.path.join(directory, file)
                        log.info(f"Found CSV file: {self.file_path}")
                        file_found = True
                        break
                if not file_found:
                    log.error(f"No CSV file found in directory: {directory}")
                    self.file_path = ""
            
        if not self.file_path:
            log.error("No file path provided for CSV extraction.")
            return False
        return True

    def extract(self) -> dict:
        # Extract data from CSV file
        try:
            with open(self.file_path, "r", encoding=self.encoding) as file:
                lines = file.readlines()
            header = lines[0].strip().split(self.delimiter)
            data = []
            for line in lines[1:]:
                values = line.strip().split(self.delimiter)
                record = {header[i]: values[i] for i in range(len(header))}
                data.append(record)

            if self.debug:
                self.save_debug_data({"raw_data": data})

            if self.save_path:
                # Move file to save path
                import shutil
                shutil.move(self.file_path, self.save_path)
                log.info(f"Moved file to {self.save_path}")
            mapped_data = []
            for record in data:
                mapped_record = {self.mapping.get(k, k): v for k, v in record.items()}
                mapped_data.append(mapped_record)
            result = {"items": mapped_data}
            if self.debug:
                self.save_debug_data_mapped(result)
            return result
        except Exception as e:
            log.error(f"Error extracting data from CSV file: {e}")
            return {}
    

