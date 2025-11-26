########################################################################################################################
# Factory for the ETLLoad classes
########################################################################################################################
import json
from scripts.classes.ETLLoad.ETLLoadBase import ETLLoadBase
from scripts.classes.ETLLoad.ETLLoadBase import ETLLoadBase
from scripts.classes.ETLLoad.ETLLoadD3BusinessObjects import ETLLoadD3BusinessObjects
from scripts.classes.ETLLoad.ETLLoadMSSQL import ETLLoadMSSQL
from scripts.classes.ETLLoad.ETLLoadCSV import ETLLoadCSV


class ETLLoadFactory:
    """
    Factory class to create ETLLoad instances based on configuration.
    """
    @staticmethod
    def create_loader(config: dict) -> ETLLoadBase:
        loader_type = config.get("type")
        if loader_type == "d3businessobjects":
            return ETLLoadD3BusinessObjects(config)
        elif loader_type == "mssql":
            return ETLLoadMSSQL(config)
        elif loader_type == "csv":
            return ETLLoadCSV(config)
        else:
            raise ValueError(f"Unknown ETLLoad type: {loader_type}")
