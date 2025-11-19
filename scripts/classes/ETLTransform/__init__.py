########################################################################################################################
# Factory for the ETLTransform classes
########################################################################################################################
import json
from scripts.classes.ETLLoad.ETLLoadBase import ETLLoadBase
from scripts.classes.ETLTransform.ETLTransformBase import ETLTransformBase
from scripts.classes.ETLTransform.ETLTransformHookFunction import ETLTransformHookFunction

class ETLTransformFactory:
    """
    Factory class to create ETLTransform instances based on configuration.
    """
    @staticmethod
    def create_transformer(config: dict) -> ETLTransformBase:
        transform_type = config.get("type")
        if transform_type == "hookfunction":
            return ETLTransformHookFunction(config)
        else:
            raise ValueError(f"Unknown ETLTransform type: {transform_type}")
