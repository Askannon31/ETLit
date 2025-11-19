########################################################################################################################
# Base class for ETL Extract                                                                                           #         
########################################################################################################################
import datetime
import json
import logging
import requests


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)

########################################################################################################################
# ETLExtractBase                                                                                                       #         
########################################################################################################################
class ETLExtractBase:
    def __init__(self, config):
        self.config = config

    def __str__(self):
        return f"ETLExtractBase with config: {self.config}"

    def setup(self) -> bool:
        raise NotImplementedError("Setup method must be implemented by subclasses.")

    def extract(self) -> dict:
        raise NotImplementedError("Extract method must be implemented by subclasses.")
    
    def save_debug_data(self, data: dict):
        """
        Saves the extracted data to a debug file
        """
        import json
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        debug_file: str = f"debug/{self.name}_{now}_debug_data.json"
        with open(debug_file, "w") as f:
            json.dump(data, f, indent=4)
        log.debug(f"Saved debug data to {debug_file}")
    
    def save_debug_data_mapped(self, data: dict):
        """
        Saves the mapped data to a debug file
        """
        import json
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        debug_file: str = f"debug/{self.name}_{now}_debug_mapped_data.json"
        with open(debug_file, "w") as f:
            json.dump(data, f, indent=4)
        log.debug(f"Saved debug data to {debug_file}")
