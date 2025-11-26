########################################################################################################################
# Class to Load data into a CSV File.                                                                                  #
########################################################################################################################
import logging
import csv
import os
from pathlib import Path

from scripts.classes.ETLLoad.ETLLoadBase import ETLLoadBase


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)

class ETLLoadCSV(ETLLoadBase):
    """
    Class to Load data into a CSV File.
    Inherits from ETLLoadBase.
    """

    def __init__(self, config: dict):
        """
        Initialize the ETLLoadCSV class with configuration parameters.

        :param config: Configuration dictionary containing CSV parameters.
        """
        super().__init__(config)
        self.path = config.get('path', 'data/output')
        self.filename = config.get('filename', 'output.csv')
        self.delimiter = config.get('delimiter', ',')
        self.header = config.get('header', True)
        self.mapping = config.get('mappings', {})
        self.overwrite = config.get('overwrite', True)
        self.full_path = os.path.join(self.path, self.filename)

    def setup(self) -> bool:
        """
        Setup the CSV file path and verify directory exists.
        Create directory if it doesn't exist.
        """
        try:
            # Create directory if it doesn't exist
            Path(self.path).mkdir(parents=True, exist_ok=True)
            log.info(f"Output directory '{self.path}' is ready.")
            
            # Check if file exists
            if os.path.exists(self.full_path):
                if self.overwrite:
                    log.info(f"CSV file '{self.full_path}' exists and will be overwritten.")
                else:
                    log.info(f"CSV file '{self.full_path}' exists and will be appended.")
            else:
                log.info(f"CSV file '{self.full_path}' will be created.")
            
            return True
        except Exception as e:
            log.error(f"Setup failed: {e}")
            return False

    def load(self, data: dict) -> bool:
        """
        Load data into the CSV file.
        
        :param data: Dictionary containing 'items' list with data to write
        :return: True if successful, False otherwise
        """
        try:
            items = data.get('items', [])
            
            if not items:
                log.warning("No items to write to CSV file.")
                return True
            
            # Determine fieldnames from mapping or from first item
            if self.mapping:
                # Use mapping to determine column order
                fieldnames = list(self.mapping.values())
            else:
                # Use keys from first item
                fieldnames = list(items[0].keys())
            
            # Determine write mode
            file_exists = os.path.exists(self.full_path)
            mode = 'w' if (self.overwrite or not file_exists) else 'a'
            write_header = self.header and (mode == 'w' or not file_exists)
            
            # Write data to CSV
            with open(self.full_path, mode=mode, newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=self.delimiter, extrasaction='ignore')
                
                if write_header:
                    writer.writeheader()
                    log.debug(f"CSV header written: {fieldnames}")
                
                # Write each item
                for item in items:
                    # Apply mapping if defined
                    if self.mapping:
                        mapped_item = {}
                        for source_field, target_field in self.mapping.items():
                            mapped_item[target_field] = item.get(source_field, '')
                        writer.writerow(mapped_item)
                    else:
                        writer.writerow(item)
                
                log.info(f"Successfully wrote {len(items)} records to '{self.full_path}'.")
            
            return True
        except Exception as e:
            log.error(f"Load failed: {e}")
            return False