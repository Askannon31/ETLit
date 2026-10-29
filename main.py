####################################################################################################
#                                      ETLit                                                       #
#                                      Author:   XGWSLIT                                           #
#                                      Version:  0.1                                               #
#                                      Date:     2025-11-12                                        #
####################################################################################################

####################################################################################################
#                                           Imports                                                #
####################################################################################################
import argparse
import importlib.util
import json
import logging
import logging.config
from pathlib import Path
import time


from scripts.utils.logger import setup_logger


####################################################################################################
#                                          Functions                                               #
####################################################################################################
def load_config(config_filename: str) -> dict:
    config_directory = Path(__file__).resolve().parent / "config"
    filename = Path(config_filename)

    if filename.name != config_filename or filename.suffix != ".py":
        raise ValueError("Provide a Python config filename located directly in the config folder.")

    config_path = (config_directory / filename).resolve()
    if config_path.parent != config_directory.resolve():
        raise ValueError("The config file must be located directly in the config folder.")
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    spec = importlib.util.spec_from_file_location(f"_etlit_config_{filename.stem}", config_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load config file: {config_path}")

    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    return config_module.config


####################################################################################################
#                                            Setup                                                 #
####################################################################################################
# Loat .env file
from dotenv import load_dotenv
load_dotenv()


# Load Config

# Setup Logger
with open("config/logging.json", "rt") as file:
    logger_config = json.load(file)
logging.config.dictConfig(logger_config)
log = logging.getLogger(__name__)

####################################################################################################
#                                            Script                                                #
####################################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ETLit with a selected configuration.")
    parser.add_argument(
        "config_file",
        nargs="?",
        default="config.py",
        help="Python config filename from the config folder (default: config.py)",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config_file)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

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
                extract_start_time = time.time()
                data = extractor.extract()
                extract_end_time = time.time()
                extract_duration = extract_end_time - extract_start_time
                log.info(f"Extracted data for process {process_name}: {len(data.get('items', []))} items")
                log.info(f"Extraction duration for process {process_name}: {extract_duration:.2f} seconds")
            else:
                log.error(f"Extractor setup failed for process: {process_name}")
                continue
        except Exception as e:
            log.error(f"Exception during extraction for process {process_name}: {e}")
            continue

        # ETL Transform
        transform_config: dict = process_config.get("transformation", {})
        # Only perform transformation if config is provided
        if not transform_config:
            log.info(f"No transformation configuration provided for process: {process_name}. Skipping transformation.")
        else:
            try:
                from scripts.classes.ETLTransform import ETLTransformFactory
                transformer = ETLTransformFactory.create_transformer(transform_config)
                log.info(f"Created transformer: {transformer}")
                if transformer.setup():
                    log.info(f"Transformer setup successful for process: {process_name}")
                    if data is not None:
                        transform_start_time = time.time()
                        data = transformer.transform(data)
                        transform_end_time = time.time()
                        transform_duration = transform_end_time - transform_start_time
                        log.info(f"Tranpipsformed data for process {process_name}: {len(data.get('items', []))} items")
                        log.info(f"Transformation duration for process {process_name}: {transform_duration:.2f} seconds")
                    else:
                        log.error(f"No data to transform for process: {process_name}")
                else:
                    log.error(f"Transformer setup failed for process: {process_name}")
                    continue
            except Exception as e:
                log.error(f"Exception during transformation for process {process_name}: {e}")
                continue

        # ETL Load
        load_config: dict = process_config.get("loading", {})
        try:
            from scripts.classes.ETLLoad import ETLLoadFactory

            loader = ETLLoadFactory.create_loader(load_config)
            log.info(f"Created loader: {loader}")

            if loader.setup():
                log.info(f"Loader setup successful for process: {process_name}")
                if data is not None:
                    load_start_time = time.time()
                    load_result = loader.load(data)
                    load_end_time = time.time()
                    load_duration = load_end_time - load_start_time
                    log.info(f"Loaded data for process {process_name}:")
                    log.info(f"Load duration for process {process_name}: {load_duration:.2f} seconds")
                else:
                    log.error(f"No data to load for process: {process_name}")
            else:
                log.error(f"Loader setup failed for process: {process_name}")
        except Exception as e:
            log.error(f"Exception occurred while loading data for process {process_name}: {e}")
