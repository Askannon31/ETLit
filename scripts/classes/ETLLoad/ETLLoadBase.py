########################################################################################################################
# Base class for ETL Load                                                                                              #
########################################################################################################################
class ETLLoadBase:
    def __init__(self, config):
        self.config = config

    def __str__(self):
        return f"ETLLoadBase with config: {self.config}"

    def setup(self) -> bool:
        raise NotImplementedError("Setup method must be implemented by subclasses.")

    def load(self, data: dict) -> bool:
        raise NotImplementedError("Load method must be implemented by subclasses.")