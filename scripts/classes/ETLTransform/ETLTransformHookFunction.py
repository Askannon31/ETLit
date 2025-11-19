###################################################################################################
# ETLTransformHookFunction to execute a custom hook function for data transformation              #
###################################################################################################
import logging

from scripts.classes.ETLTransform.ETLTransformBase import ETLTransformBase


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)


class ETLTransformHookFunction(ETLTransformBase):
    """
    ETL Transform class to execute a custom hook function for data transformation.
    Inherits from ETLTransformBase.
    """

    def __init__(self, config):
        """
        Initialize ETLTransformHookFunction with configuration.

        Args:
            config (dict): Configuration dictionary for the transform.
        """
        super().__init__(config)
        self.name = config.get("name", "ETLTransformHookFunction")
        self.hook_file = config.get("hook_file", "")
        self.function_name = config.get("function_name", "")
        self.debug = config.get("debug", False)
        self.config = config.get("config", {})

        log.info(f"Initialized ETLTransformHookFunction with hook file: {self.hook_file} and function: {self.function_name}")

    def transform(self, data: dict) -> dict:
        """
        Execute the custom hook function to transform data.

        Args:
            data (dict): Dictionary of data items to be transformed.

        Returns:
            dict: Transformed data items.
        """
        try:
            # Dynamically import the hook function
            import importlib.util
            spec = importlib.util.spec_from_file_location("transform_hooks", self.hook_file)
            hook_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hook_module)

            hook_function = getattr(hook_module, self.function_name)

            # Execute the hook function
            transformed_data = hook_function(data, self.config)
            log.info(f"Data transformed using hook function: {self.function_name}")
            if self.debug:
                self.save_debug_data(transformed_data)
            return transformed_data

        except Exception as e:
            log.error(f"Error executing hook function '{self.function_name}': {e}")
            return data  # Return original data in case of error


    def setup(self) -> bool:
        """
        Setup method for ETLTransformHookFunction.
        Checks if the hook file exists and the function name is provided.
        Returns:
            bool: True if setup is successful, False otherwise.
        """
        import os
        if not os.path.isfile(self.hook_file):
            log.error(f"Hook file does not exist: {self.hook_file}")
            return False

        if not self.function_name:
            log.error("Function name is not specified in configuration.")
            return False

        log.info("ETLTransformHookFunction setup completed successfully.")
        return True

