########################################################################################################################
# Class to extract data from the gevis api. Either the base BC API or the custom gevisECM API.                         #         
########################################################################################################################
import logging
import requests

########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)


########################################################################################################################
#                                                  ETLExtractGevisApi                                                  #
########################################################################################################################
class ETLExtractGevisApi():
    def __init__(self, config):
        self.config = config
        self.name = config.get("name", "ETLExtractGevisApi")
        self.api = {
            "base_url": config.get("base_url", ""),
            "erp_tenant_id": config.get("erp_tenant_id", ""),
            "client_id": config.get("authorization", None).get("client_id", ""),
            "client_secret": config.get("authorization", None).get("client_secret", ""),
            "endpoint": config.get("api_endpoints", ""),
            "query_parameters": config.get("query_parameters", {}),
            "token": None
        }
        self.mapping = config.get("mapping", {})
        log.info(f"Initialized ETLExtractGevisApi with name: {self.name}")

    def __str__(self):
        return f"ETLExtractGevisApi({self.name})"

    def setup(self) -> bool:
        log.debug(f"Setting up {self}")
        try:
            api_token: str = self.get_access_token()
            if api_token != None and api_token != "":
                self.api["token"] = api_token
                log.info(f"Successfully retrieved API token for {self}")
                return True
            else:
                log.error(f"Failed to retrieve API token for {self}")
                return False
        except Exception as e:
            log.error(f"Exception during setup of {self}: {e}")
            return False
    
    def get_access_token(self) -> str:
        """
        Retrieves the access token from Microsoft via the configuration
        """
        erpTenantId: str = self.api["erp_tenant_id"]
        url: str = f"https://login.microsoftonline.com/{erpTenantId}/oauth2/v2.0/token"
        response = requests.post(
            url,
            data={
                "grant_type": "client_credentials",
                "scope": "https://api.businesscentral.dynamics.com/.default"
            },
            auth=(self.api["client_id"], self.api["client_secret"]),
        )
        return response.json()["access_token"]

    def extract(self) -> dict:
        raise NotImplementedError("Extract method must be implemented by subclasses.")
