########################################################################################################################
# Factory for the ETLExtract classes
########################################################################################################################
import json
from scripts.classes.ETLExtract.ETLExtractBase import ETLExtractBase
from scripts.classes.ETLExtract.ETLExtractGevisApi import ETLExtractGevisApi
from scripts.classes.ETLExtract.ETLExtractCSVFile import ETLExtractCSVFile


class ETLExtractFactory:
    """
    Factory class to create ETLExtract instances based on configuration.
    """
    @staticmethod
    def create_extractor(config: dict) -> ETLExtractBase:
        extractor_type = config.get("type")
        if extractor_type == "gevisapi":
            return ETLExtractGevisApi(config)
        elif extractor_type == "csvfile":
            return ETLExtractCSVFile(config)
        else:
            raise ValueError(f"Unknown ETLExtract type: {extractor_type}")
