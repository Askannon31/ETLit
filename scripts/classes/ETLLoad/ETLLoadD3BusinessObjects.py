########################################################################################################################
# Class to Load data into the D3 Business Objects system.                                                              #
########################################################################################################################
import logging

import requests

from scripts.classes.ETLLoad.ETLLoadBase import ETLLoadBase


########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
log = logging.getLogger(__name__)

class ETLLoadD3BusinessObjects(ETLLoadBase):
    def __init__(self, config):
        super().__init__(config)
        self.name = config.get("name", "ETLLoadD3BusinessObjects")
        self.base_url = config.get("base_url", "")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "")
        self.entity = {
            "name": config.get("entity", {}).get("name", ""),
            "plural": config.get("entity", {}).get("pluralName", ""),
            "definition": config.get("entity", {}).get("definition", {})
        }

        log.info(f"Initialized ETLLoadD3BusinessObjects with name: {self.name}")
    
    
    def __str__(self):
        return f"ETLLoadD3BusinessObjects({self.name})"

    def setup(self) -> bool:
        # Setup logic for D3 Business Objects
        try:
            model_exists, model_info = self.check_model_exists()
            log.debug(f"Model exists: {model_exists}, Model info: {model_info}")
            if not model_exists:
                log.error(f"Model '{self.model}' does not exist in D3 Business Objects.")
                return False
            log.info(f"Model '{self.model}' exists in D3 Business Objects.")
            entity_exists, entity_info = self.check_entity_exists(model_info)
            if not entity_exists:
                log.error(f"Entity '{self.entity['name']}' does not exist in model '{self.model}'.")
                created = self.create_entity()
                if not created:
                    log.error(f"Failed to create entity '{self.entity['name']}' in model '{self.model}'.")
                    return False
                log.info(f"Entity '{self.entity['name']}' created successfully in model '{self.model}'.")
                return True
            log.debug(f"Entity exists: {entity_exists}, Entity info: {entity_info}")
        except Exception as e:
            log.error(f"Error during setup of ETLLoadD3BusinessObjects: {e}")
            return False
        return True
    
    def check_model_exists(self) -> tuple[bool, dict]:
        # Check if the model exists in D3 Business Objects
        url: str = f"/businessobjects/core/models/customModels"
        success, response = self.execute_request("GET", url)
        if success:
            log.debug(f"Model check response: {response}")
            for model in response.get("value", []):
                model_name = model.get("name", "")
                log.debug(f"Checking model: {model_name}")
                if model_name == self.model:
                    model_id = model.get("id", "")
                    log.info(f"Model '{self.model}' exists with ID: {model_id}")
                    self.model_id = model_id
                    return True, model
    
    def check_entity_exists(self, model_data: dict) -> tuple[bool, dict]:
        log.debug(f"Checking for entity '{self.entity['name']}' in model data.")
        entities = model_data.get("entityTypes", [])
        log.debug(f"Entities in model: {len(entities)}")
        for entity in entities:
            entity_name = entity.get("name", "")
            log.debug(f"Checking entity: {entity_name}")
            if entity_name == self.entity["name"]:
                log.info(f"Entity '{self.entity['name']}' exists in model '{self.model}'.")
                return True, entity
        log.info(f"Entity '{self.entity['name']}' does not exist in model '{self.model}'.")
        return False, {}

    def create_entity(self) -> bool:
        # Create entity in D3 Business Objects
        url: str = f"/businessobjects/core/models/customModels/{self.model_id}/entityTypes"
        data: dict = self.entity["definition"]
        success, response = self.execute_request("POST", url, data)
        if not success:
            log.error(f"Failed to create entity '{self.entity['name']}' in model '{self.model}'.")
            return False
        log.info(f"Entity '{self.entity['name']}' created successfully in model '{self.model}'.")

        return True

    
    def execute_request(self, method: str, endpoint: str, data: dict = None) -> tuple[bool, dict]:
        # Execute HTTP request to D3 Business Objects API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        if data:
            headers["Content-Type"] = "application/json"
        try:
            if method.upper() == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method.upper() == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data)
            else:
                log.error(f"Unsupported HTTP method: {method}")
                return False, {}

            if response.status_code in [200, 201]:
                return True, response.json()
            if response.status_code == 204:
                return True, {}
            else:
                log.error(f"Request to {endpoint} failed with status code {response.status_code}: {response.text}")
                return False, {}
        except Exception as e:
            log.error(f"Exception during request to {endpoint}: {e}")
        return True, {}
        


    def load(self, data: dict) -> bool:
        # Load data into D3 Business Objects
        return True