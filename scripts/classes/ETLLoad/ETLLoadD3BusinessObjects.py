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
            "plural": config.get("entity", {}).get("definition", {}).get("pluralName", ""),
            "definition": config.get("entity", {}).get("definition", {})
        }
        self.batch_size = config.get("batch_size", 1)
        self.truncate_entity_before_load = config.get("truncate_before_load", False)
        self.mapping = config.get("mapping", {})

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
            elif method.upper() == "PUT":
                response = requests.put(f"{self.base_url}{endpoint}", headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(f"{self.base_url}{endpoint}", headers=headers)
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
        return False, {}

    def build_batch_request(self, items: list, entity_key_field: str, entity_key_type: str = "String") -> list:
        """
        Build batch request payload for Business Objects API.
        
        Args:
            items: List of items to upload
            entity_key_field: The field name that contains the entity key
            entity_key_type: Type of the entity key (String, Guid, Int32, Int64)
        
        Returns:
            List of request objects for batch processing
        """
        requests = []
        
        for idx, item in enumerate(items, start=1):
            # Get the key value from the item
            key_value = item.get(entity_key_field)
            if not key_value:
                log.warning(f"Item {idx} missing entity key field '{entity_key_field}', skipping")
                continue
            
            # Format the key based on type
            if entity_key_type == "String":
                key_formatting = f"('{key_value}')"
            elif entity_key_type in ["Guid", "Int32", "Int64"]:
                key_formatting = f"({key_value})"
            else:
                log.error(f"Unsupported entity key type: {entity_key_type}")
                continue
            
            # Build the request object
            request = {
                "id": str(idx),
                "method": "PUT",
                "url": f"{self.entity['plural']}{key_formatting}",
                "body": item,
                "headers": {
                    "content-type": "application/json"
                }
            }
            
            requests.append(request)
        
        return requests

    def execute_batch_request(self, requests: list) -> tuple[bool, dict]:
        """
        Execute a batch request to Business Objects API.
        
        Args:
            requests: List of request objects
        
        Returns:
            Tuple of (success, response)
        """
        if not requests:
            log.warning("No requests to execute in batch")
            return True, {}
        
        # Build the batch payload
        batch_payload = {
            "requests": requests
        }
        
        log.info(f"Executing batch request with {len(requests)} items")
        log.debug(f"Batch payload: {batch_payload}")
        
        # Execute the batch request - batch endpoint is at model level, not entity level
        endpoint = f"/businessobjects/custom/{self.model}/$batch"
        success, response = self.execute_request("POST", endpoint, batch_payload)
        
        if success:
            log.info(f"Batch request executed successfully")
            
            # Check individual responses for errors
            if isinstance(response, dict) and "responses" in response:
                for resp in response.get("responses", []):
                    status = resp.get("status")
                    if status not in [200, 201, 204]:
                        log.warning(f"Batch item {resp.get('id')} failed with status {status}: {resp.get('body')}")
            
            return True, response
        else:
            log.error(f"Batch request failed")
            return False, response

    def load(self, data: dict) -> bool:
        """
        Load data into D3 Business Objects using batch processing.
        
        Args:
            data: Dictionary containing 'items' list and metadata
        
        Returns:
            True if successful, False otherwise
        """
        log.info(f"Loading data into D3 Business Objects using {self}")
        
        items = data.get('items', [])
        log.info(f"Data to load: {len(items)} items")
        
        if not items:
            log.warning("No items to load")
            return True
        
        if self.truncate_entity_before_load:
            truncated = self.truncate_entity()
            if not truncated:
                log.error("Failed to truncate entity before load")
                return False
        
        # Get entity key configuration from config or use default
        entity_key_field = data.get('entity_key_field', 'id')
        entity_key_type = data.get('entity_key_type', 'String')
        
        log.debug(f"Entity key field: {entity_key_field}, type: {entity_key_type}")
        
        # Process items in batches
        batch_size = self.batch_size if self.batch_size > 0 else 100
        total_items = len(items)
        success_count = 0
        
        for i in range(0, total_items, batch_size):
            batch = self.apply_mapping(items[i:i + batch_size])
            batch_num = (i // batch_size) + 1
            total_batches = (total_items + batch_size - 1) // batch_size
            
            log.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
            
            # Build batch requests
            requests = self.build_batch_request(batch, entity_key_field, entity_key_type)
            
            if not requests:
                log.warning(f"No valid requests in batch {batch_num}, skipping")
                continue
            
            # Execute batch request
            success, response = self.execute_batch_request(requests)
            
            if success:
                success_count += len(requests)
                log.info(f"Batch {batch_num} completed successfully")
            else:
                log.error(f"Batch {batch_num} failed")
                return False
        
        log.info(f"Successfully loaded {success_count}/{total_items} items")
        return True
    
    def apply_mapping(self, items: list) -> list:
        """
        Apply mapping to a single item.
        
        Args:
            item: The original item dictionary
            mapping: The mapping dictionary
        
        Returns:
            Mapped item dictionary
        """
        mapped_items = []
        for item in items:
            mapped_item = {}
            for source_field, target_field in self.mapping.items():
                mapped_item[target_field] = item.get(source_field)
            mapped_items.append(mapped_item)
        return mapped_items

    def truncate_entity(self) -> bool:
        """
        Truncate the entity data before loading new data.
        
        Returns:
            True if successful, False otherwise
        """
        log.info(f"Truncating entity '{self.entity['name']}' in model '{self.model}'")
        
        # Build the delete request payload
        url: str = f"/businessobjects/custom/{self.model}/bo.clearEntitySet"

        payload: dict = {
            "entitySet": self.entity["plural"],
            "mode": "truncate"
        }
        
        success, response = self.execute_request("POST", url, payload)
        
        if success:
            log.info(f"Entity '{self.entity['name']}' truncated successfully")
            return True
        else:
            log.error(f"Failed to truncate entity '{self.entity['name']}'")
            return False
