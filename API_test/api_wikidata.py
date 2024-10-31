# Wikidata API, output like:
# {'is_in_Venice': True, 'name': 'Noale', 'coordinates': (45.55012, 12.0709)}
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
    
    if not search_results['search']:
        return None
    
    entity_id = search_results['search'][0]['id']
    
    # Step 2: Get the entity's information using its Wikidata ID
    entity_url = "https://www.wikidata.org/w/api.php"
    entity_params = {
        "action": "wbgetentities",
        "ids": entity_id,
        "props": "claims",
        "format": "json"
    }
    
    entity_response = requests.get(entity_url, params=entity_params)
    entity_data = entity_response.json()
    
    entity_info = entity_data['entities'][entity_id]
    claims = entity_info.get('claims', {})
    
    # Define relevant properties
    relevant_properties = {
        'P17': 'Country',
        'P131': 'Province',
        'P291': 'Locale',
        'P625': 'Geography',
        'P150': 'Metropolitan City',
        'P36': 'Capital'
    }
    
    # Initialize output structure dynamically
    output = {label: [] for _, label in relevant_properties.items()}
    output.update({key: 'Unknown' for key in relevant_properties.values()})
    
    for prop, label in relevant_properties.items():
        if prop in claims:
            if prop == 'P625':  # Handling Geography separately for coordinates
                for item in claims[prop]:
                    lat = item['mainsnak']['datavalue']['value']['latitude']
                    lon = item['mainsnak']['datavalue']['value']['longitude']
                    output['Geography'] = [f"{lat}, {lon}"]  # Set Geography as a list with one item
            else:
                # Collecting other location-related information
                item_ids = [item['mainsnak']['datavalue']['value']['id'] for item in claims[prop]]
                labels = get_labels_by_ids(item_ids)
                if labels:
                    output[label] = labels  # Collecting all labels
    
    # Check and format Locale specifically
    if output['Locale'] == 'Unknown':
        if output['Province'] != 'Unknown':
            output['Locale'] = f"{output['Province']}, Italy"

    # Print the output for debugging before checking for Venice
    print("Output before checking for Venice:", output)

    # Check if any location information contains Venice
    is_in_venice = any(
        ("venice" in str(label).lower()) 
        for key, values in output.items() 
        for label in (values if isinstance(values, list) else [values])
    )
    
    # Prepare final output
    final_output = {
        "is_in_Venice": is_in_venice,
        "name": entity_name
    }
    
    # Add coordinates if the entity is in Venice
    if is_in_venice and output['Geography']:
        final_output['coordinates'] = tuple(map(float, output['Geography'][0].split(',')))
    
    return final_output

def get_labels_by_ids(q_ids):
    # Fetch labels for Q identifiers
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

    # Check if 'entities' key exists
    if 'entities' not in label_data:
        print("Error fetching labels:", label_data)  # Print the response for debugging
        return []

    # Create a list of labels
    labels = []
    for entity_id, entity in label_data['entities'].items():
        labels.append(entity.get('labels', {}).get('en', {}).get('value', entity_id))

    return labels

# Example usage
entity_name = "Venice"  # You can test with other entities as well
info = get_wikidata_info(entity_name)
print(info)
