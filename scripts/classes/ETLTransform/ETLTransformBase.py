########################################################################################################################
# Base class for ETL Transform                                                                                         #
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
# ETLTransformBase                                                                                         #
########################################################################################################################
class ETLTransformBase:
    def __init__(self, config):
        self.config = config

    def __str__(self):
        return f"ETLTransformBase with config: {self.config}"

    def setup(self) -> bool:
        raise NotImplementedError("Setup method must be implemented by subclasses.")

    def transform(self, data: dict) -> dict:
        raise NotImplementedError("Transform method must be implemented by subclasses.")

    def save_debug_data(self, data: dict):
        """
        Saves the extracted data to a debug file
        """
        import json
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        debug_file: str = f"debug/{self.name}_{now}_debug_data_transform.json"
        with open(debug_file, "w") as f:
            json.dump(data, f, indent=4)
        log.debug(f"Saved debug data to {debug_file}")