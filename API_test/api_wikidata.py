import requests

def get_wikidata_info(entity_name):
    # Step 1: Search for the entity to get its Wikidata ID
    search_url = "https://www.wikidata.org/w/api.php"
    search_params = {
        "action": "wbsearchentities",
        "search": entity_name,
        "language": "en",
        "format": "json"
    }
    
    response = requests.get(search_url, params=search_params)
    search_results = response.json()
    
    # List of keywords to check for, related to Venice
    venice_keywords = ["venice", "venetian", "venitian"]
    
    # # Print all search results to help identify the correct ID
    # print("Search results:")
    # for result in search_results['search']:
    #     print(f"ID: {result['id']}, Label: {result['label']}, Description: {result.get('description', 'No description')}")
    
    # List to hold all entity IDs that mention Venice-related keywords
    relevant_entity_ids = []
    
    # Loop through the search results and find entities mentioning Venice-related keywords
    for result in search_results['search']:
        description = result.get("description", "").lower()
        if any(keyword in description for keyword in venice_keywords):
            relevant_entity_ids.append(result['id'])
    
    if not relevant_entity_ids:
        # print("Could not find any entities mentioning Venice-related keywords.")
        return None
    
    # Step 2: Get the entities' information using their Wikidata IDs
    entities_info = []
    
    for entity_id in relevant_entity_ids:
        entity_url = "https://www.wikidata.org/w/api.php"
        entity_params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "props": "claims|labels",  # Include labels in the API request
            "format": "json"
        }
        
        entity_response = requests.get(entity_url, params=entity_params)
        entity_data = entity_response.json()
        
        # # Print the entire claims and labels data to inspect it
        # print(f"Claims data for Entity ID: {entity_id}:")
        # print(entity_data)
        
        # Extract claims from the entity data
        entity_info = entity_data['entities'][entity_id]
        claims = entity_info.get('claims', {})
        
        # Safely extract labels
        entity_label = entity_info.get('labels', {}).get('en', {}).get('value', 'Unknown')
        
        # Define relevant properties including Administration
        relevant_properties = {
            'P17': 'Country',
            'P131': 'Province',
            'P291': 'Locale',
            'P625': 'Geography',
            'P150': 'Metropolitan City',
            'P36': 'Capital',
            'P131_Admin': 'Administration'  # Using P131 again to capture administration levels
        }
        
        # Initialize output structure dynamically
        output = {label: 'Unknown' for _, label in relevant_properties.items()}
        output['Geography'] = []  # Ensure Geography is a list to store coordinates

        for prop, label in relevant_properties.items():
            if prop in claims:
                if prop == 'P625':  # Handling Geography for coordinates
                    for item in claims[prop]:
                        lat = item['mainsnak']['datavalue']['value']['latitude']
                        lon = item['mainsnak']['datavalue']['value']['longitude']
                        output['Geography'] = [f"{lat}, {lon}"]
                else:
                    # Collecting other location-related information
                    item_ids = [item['mainsnak']['datavalue']['value']['id'] for item in claims[prop]]
                    labels = get_labels_by_ids(item_ids)
                    if labels:
                        output[label] = labels  # Store all labels found

        # Check if any location information contains "Venice"
        is_in_venice = any(
            "venice" in str(value).lower() 
            for key, value in output.items() 
            if isinstance(value, str) or isinstance(value, list)  # Check lists and strings
            for label in (value if isinstance(value, list) else [value])
        )
        
        # Prepare the result for this entity
        entity_result = {
            "is_in_Venice": is_in_venice,
            "name": entity_label  # Use the safely extracted label
        }
        
        # Add coordinates if the entity is in Venice
        if is_in_venice and output['Geography']:
            entity_result['coordinates'] = tuple(map(float, output['Geography'][0].split(',')))
        
        # Only append to the results if the entity is in Venice
        if is_in_venice:
            entities_info.append(entity_result)

    # Return only the entities that are in Venice
    return entities_info

def get_labels_by_ids(q_ids):
    if not q_ids:
        return []

    q_ids_str = '|'.join(q_ids)
    label_url = "https://www.wikidata.org/w/api.php"
    label_params = {
        "action": "wbgetentities",
        "ids": q_ids_str,
        "props": "labels",
        "format": "json",
        "languages": "en"
    }

    label_response = requests.get(label_url, params=label_params)
    label_data = label_response.json()

    if 'entities' not in label_data:
        print("Error fetching labels:", label_data)
        return []

    labels = []
    for entity_id, entity in label_data['entities'].items():
        labels.append(entity.get('labels', {}).get('en', {}).get('value', entity_id))

    return labels

# # Example usage
# entity_name = "Rialto Bridge"
# info = get_wikidata_info(entity_name)
# print(info)

def wikidata_is_in_venice(location_name):
    # Call get_wikidata_info and format the output
    info = get_wikidata_info(location_name)
    
    if info:
        # Return all entities that might be in Venice, with coordinates if available
        return info
    else:
        return None
