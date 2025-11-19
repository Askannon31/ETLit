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
        company_code = "Raiff. Delbrück"
        transformed_item["company"] = company_code
        
        transformed_items.append(transformed_item)
    
    # Filter items:
    # Many entries have the save "no" and "dmsNo" -> keep only the latest modified one
    filtered_items = {}
    for item in transformed_items:
        key = (item.get("no"), item.get("dmsNo"))
        existing_item = filtered_items.get(key)
        if existing_item is None or item.get("systemModifiedAt", "") > existing_item.get("systemModifiedAt", ""):
            filtered_items[key] = item

    return {"items": list(filtered_items.values())}