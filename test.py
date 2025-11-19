####################################################################################################
#                                      ETLit                                                       #
#                                      Author:   XGWSLIT                                           #
#                                      Version:  0.1                                               #
#                                      Date:     2025-11-12                                        #
####################################################################################################

####################################################################################################
#                                           Imports                                                #
####################################################################################################
import json
import logging
import logging.config

from scripts.utils.logger import setup_logger


####################################################################################################
#                                          Functions                                               #
####################################################################################################


####################################################################################################
#                                            Setup                                                 #
####################################################################################################
# Loat .env file
from dotenv import load_dotenv
load_dotenv()


# Load Config
from config.config import config


# Setup Logger
with open("config/logging.json", "rt") as file:
    logger_config = json.load(file)
logging.config.dictConfig(logger_config)
log = logging.getLogger(__name__)

####################################################################################################
#                                            Script                                                #
####################################################################################################
if __name__ == "__main__":
    log.info("-------------------- Start Script --------------------")
    processes: list = config.get("ETL", {}).get("processes", [])
    log.info(f"Loaded {len(processes)} processes from configuration.")

    for process_config in processes:
        process_name: str = process_config.get("name", "UnnamedProcess")
        log.info(f"Starting process: {process_name}")

        # ETL Extract
        extract_config: dict = process_config.get("extraction", {})
        data: dict = None
        
        with open("debug\Delbrueck Item Ledger Entries_2025-11-19_08-27-42_debug_mapped_data.json", "rt") as file:
            data = json.load(file)
        log.info(f"Extracted {len(data.get('mapped_data', []))} items from source.")

        # ETL Load
        load_config: dict = process_config.get("loading", {})
        try:
            from scripts.classes.ETLLoad import ETLLoadFactory

            loader = ETLLoadFactory.create_loader(load_config)
            log.info(f"Created loader: {loader}")

            if loader.setup():
                log.info(f"Loader setup successful for process: {process_name}")
                if data is not None:
                    load_result = loader.load(data)
                    log.info(f"Loaded data for process {process_name}: {load_result}")
                else:
                    log.error(f"No data to load for process: {process_name}")
            else:
                log.error(f"Loader setup failed for process: {process_name}")
        except Exception as e:
            log.error(f"Exception occurred while loading data for process {process_name}: {e}")
