########################################################################################################################
# Class to extract data from the gevis api. Either the base BC API or the custom gevisECM API.                         #         
########################################################################################################################
import datetime
import json
import logging
import requests

from scripts.classes.ETLExtract import ETLExtractBase

########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)


########################################################################################################################
#                                                  ETLExtractGevisApi                                                  #
########################################################################################################################
class ETLExtractGevisApi(ETLExtractBase):
    def __init__(self, config):
        super().__init__(config)
        self.name = config.get("name", "ETLExtractGevisApi")
        self.debug = config.get("debug", False)
        self.api = {
            "base_url": config.get("base_url", ""),
            "erp_tenant_id": config.get("erp_tenant_id", ""),
            "client_id": config.get("authorization", None).get("client_id", ""),
            "client_secret": config.get("authorization", None).get("client_secret", ""),
            "endpoint": config.get("endpoint", ""),
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
            # api_token: str = "DUMMY_TOKEN_FOR_TESTING"
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
        """
        Extracts data from the Gevis API
        """
        log.debug(f"Extracting data using {self}")
        request_url: str = self.create_request_url()
        headers: dict = {
            "Authorization": f"Bearer {self.api['token']}",
            "Content-Type": "application/json"
        }
        response = requests.get(request_url, headers=headers)
        if response.status_code == 200:
            data: dict = response.json()
            log.info(f"Successfully extracted data from {self}")
            if self.debug:
                self.save_debug_data(data)

            # Execute mapping
            mapped_data = self.execute_mapping(data)
            if self.debug:
                self.save_debug_data_mapped(mapped_data)
            return mapped_data
        else:
            log.error(f"Failed to extract data from {self}. Status code: {response.status_code}")
            return {}

    def create_request_url(self) -> str:
        """
        Creates the full request URL with query parameters
        """
        base_url: str = self.api["base_url"]
        endpoint: str = self.api["endpoint"]
        query_params: dict = self.api["query_parameters"]

        # Construct query string
        query_string: str = "&".join([f"{key}={value}" for key, value in query_params.items()])
        full_url: str = f"{base_url}{endpoint}?{query_string}"
        log.debug(f"Constructed request URL: {full_url}")
        return full_url
    
    def execute_mapping(self, data: dict) -> dict:
        """
        Executes the mapping on the extracted data
        """
        log.debug(f"Executing mapping for {self}")
        mapped_data: list = []
        items: list = data.get("value", [])
        for item in items:
            mapped_item: dict = {}
            for source_field,target_field in self.mapping.items():
                mapped_item[target_field] = item.get(source_field, None)
            mapped_data.append(mapped_item)
        log.info(f"Successfully executed mapping for {self}")
        return {"items": mapped_data}
    
    

  