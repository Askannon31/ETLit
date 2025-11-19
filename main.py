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
        if not process_config.get("active", False):
            log.info(f"Skipping inactive process: {process_name}")
            continue
        log.info(f"Starting process: {process_name}")

        # ETL Extract
        extract_config: dict = process_config.get("extraction", {})
        data: dict = None
        try:
            from scripts.classes.ETLExtract import ETLExtractFactory

            extractor = ETLExtractFactory.create_extractor(extract_config)
            log.info(f"Created extractor: {extractor}")

            if extractor.setup():
                log.info(f"Extractor setup successful for process: {process_name}")
                data = extractor.extract()
                log.info(f"Extracted data for process {process_name}: {data}")
            else:
                log.error(f"Extractor setup failed for process: {process_name}")
        except Exception as e:
            log.error(f"Exception during extraction for process {process_name}: {e}")

        # ETL Transform
        # TODO: Implement transformation logic here - Currently skipping this step

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
