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


CONFIG_DIRECTORY = Path(__file__).resolve().parent / "config"
log = logging.getLogger(__name__)


####################################################################################################
#                                          Functions                                               #
####################################################################################################
def load_config(config_filename: str) -> dict:
    config_directory = CONFIG_DIRECTORY
    filename = Path(config_filename)

    if filename.name != config_filename or filename.suffix != ".py":
        # raise ValueError("Provide a Python config filename located directly in the config folder.")
        # If the filename does not has a .py extension add it and search with that filename
        if filename.suffix != ".py":
            log.debug(f"Adding .py extension to config filename: {filename}")
            filename = filename.with_suffix(".py")

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


def setup_logging() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    with open(CONFIG_DIRECTORY / "logging.json", "rt") as file:
        logger_config = json.load(file)
    logging.config.dictConfig(logger_config)


def run_config(config: dict) -> bool:
    successful = True
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
        data = None
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
                successful = False
                continue
        except Exception as e:
            log.error(f"Exception during extraction for process {process_name}: {e}")
            successful = False
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
                        successful = False
                        continue
                else:
                    log.error(f"Transformer setup failed for process: {process_name}")
                    successful = False
                    continue
            except Exception as e:
                log.error(f"Exception during transformation for process {process_name}: {e}")
                successful = False
                continue

        # ETL Load
        loading_config: dict = process_config.get("loading", {})
        try:
            from scripts.classes.ETLLoad import ETLLoadFactory

            loader = ETLLoadFactory.create_loader(loading_config)
            log.info(f"Created loader: {loader}")

            if loader.setup():
                log.info(f"Loader setup successful for process: {process_name}")
                if data is not None:
                    load_start_time = time.time()
                    load_result = loader.load(data)
                    load_end_time = time.time()
                    load_duration = load_end_time - load_start_time
                    if load_result:
                        log.info(f"Loaded data for process {process_name}:")
                    else:
                        log.error(f"Loading failed for process: {process_name}")
                        successful = False
                    log.info(f"Load duration for process {process_name}: {load_duration:.2f} seconds")
                else:
                    log.error(f"No data to load for process: {process_name}")
                    successful = False
            else:
                log.error(f"Loader setup failed for process: {process_name}")
                successful = False
        except Exception as e:
            log.error(f"Exception occurred while loading data for process {process_name}: {e}")
            successful = False

    return successful


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run ETLit with selected configurations.")
    parser.add_argument(
        "config_file",
        nargs="?",
        help="Python config filename from the config folder (default: config.py)",
    )
    parser.add_argument(
        "--execute-all",
        action="store_true",
        help="Run all Python configurations in the config folder sequentially",
    )
    args = parser.parse_args(argv)
    if args.execute_all and args.config_file is not None:
        parser.error("config_file cannot be combined with --execute-all")

    try:
        setup_logging()
    except Exception:
        log.exception("Could not initialize ETLit logging or environment.")
        return 1

    log.info("-------------------- Start Script --------------------")
    if args.execute_all:
        config_files = sorted(
            (
                path.name for path in CONFIG_DIRECTORY.glob("*.py")
                if path.is_file() and path.name != "__init__.py"
            ),
            key=lambda name: (name.casefold(), name),
        )
    else:
        config_files = [args.config_file or "config.py"]

    if not config_files:
        log.error("No Python configurations found in %s.", CONFIG_DIRECTORY)
        return 1

    failed_configs = 0
    for config_filename in config_files:
        log.info("Starting configuration: %s", config_filename)
        try:
            config = load_config(config_filename)
        except (FileNotFoundError, ValueError) as error:
            if not args.execute_all:
                parser.error(str(error))
            log.exception("Could not load configuration: %s", config_filename)
            failed_configs += 1
            continue
        except Exception:
            log.exception("Could not load configuration: %s", config_filename)
            failed_configs += 1
            continue

        try:
            successful = run_config(config)
        except Exception:
            log.exception("Exception while running configuration: %s", config_filename)
            successful = False
        if not successful:
            failed_configs += 1
            log.error("Configuration failed: %s", config_filename)
        else:
            log.info("Configuration completed: %s", config_filename)

    log.info(
        "Configuration summary: %s successful, %s failed.",
        len(config_files) - failed_configs,
        failed_configs,
    )
    return 1 if failed_configs else 0


if __name__ == "__main__":
    raise SystemExit(main())
