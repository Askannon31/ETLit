########################################################################################################################
#                                                          Setup                                                       #
########################################################################################################################
# Setup Logger
import logging
log = logging.getLogger(__name__)

def transform_items(data, config) -> dict:
    """
    A hook function to transform data items before loading into D3 Business Objects.
    
    Args:
        data (dict): Dictionary of data items to be transformed with the key items which contains the list of items to be transformed. {"items": [...]}
        
        config (dict): Configuration dictionary for transformation rules.
        
    Returns:
        dict: Transformed data items. {"items": [...]}
    """
    transformed_items = []
    for item in data.get("items", []):
        transformed_item = item.copy()
        
        # Example transformation: Add company code in a new field
        company_code = "Leder Brinkmann GmbH"
        transformed_item["company"] = company_code
        
        transformed_items.append(transformed_item)
    
    # Check each item field for "'" and replace with ""
    for item in transformed_items:
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.replace("'", "")

    return {"items": list(transformed_items)}