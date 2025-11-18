########################################################################################################################
# Base class for ETL Extract                                                                                           #         
########################################################################################################################
class ETLExtractBase:
    def __init__(self, config):
        self.config = config

    def __str__(self):
        return f"ETLExtractBase with config: {self.config}"

    def setup(self) -> bool:
        raise NotImplementedError("Setup method must be implemented by subclasses.")

    def extract(self) -> dict:
        raise NotImplementedError("Extract method must be implemented by subclasses.")
