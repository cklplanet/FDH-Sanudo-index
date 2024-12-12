import requests

# Bug fixed: 1, Venice is not a Country; 2, Veneto is not Venice
def get_label_for_id(q_id):
    """
    Fetch the label for a given Wikidata entity ID.
    """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "ids": q_id,
        "props": "labels",
        "languages": "en",
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    entity = data.get("entities", {}).get(q_id, {})
    label = entity.get("labels", {}).get("en", {}).get("value", q_id)  # Return ID if label is unavailable
    return label


def search_entity_id(entity_name):
    """
    Search for the entity on Wikidata and return a list of entity IDs found.
    """
    search_url = "https://www.wikidata.org/w/api.php"
    search_params = {
        "action": "wbsearchentities",
        "search": entity_name,
        "language": "en",
        "format": "json"
    }
    
    response = requests.get(search_url, params=search_params)
    results = response.json().get('search', [])
    
    # # Display search results for validation
    # print("Search results for verification:")
    entity_ids = []
    for result in results:
        # print(f"ID: {result['id']}, Label: {result['label']}, Description: {result.get('description', 'No description')}")
        entity_ids.append(result['id'])
    
    # # Return list of entity IDs
    # return entity_ids if entity_ids else None
    if results:
        # Return the ID of the shortest result (based on the character length of the ID)
        shortest_result = min(results, key=lambda result: len(result['id']))
        return shortest_result['id']
    return None


def get_entity_data(entity_id):
    """
    Retrieve data for an entity, focusing on specific properties.
    """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "ids": entity_id,
        "props": "claims",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    claims = data['entities'][entity_id].get('claims', {})
    
    # Dictionary to store resolved data for each property
    extracted_data = {}

    # Properties to fetch
    properties = {
        'P276': 'Location',
        'P131': 'Administrative Entity',
        'P625': 'Coordinates',
        # 'P17': 'Country',
        'P291': 'Locale',
        'P150': 'Metropolitan City',
        'P36': 'Capital'
    }

    for prop, label in properties.items():
        if prop in claims:
            if prop == 'P625':  # Handle coordinates separately
                coordinates = [
                    (item['mainsnak']['datavalue']['value']['latitude'], 
                     item['mainsnak']['datavalue']['value']['longitude'])
                    for item in claims[prop]
                    if 'datavalue' in item['mainsnak']  # Check for 'datavalue' key
                ]
                extracted_data[label] = coordinates
            else:
                # For other properties, resolve IDs to labels
                ids = [
                    item['mainsnak']['datavalue']['value']['id']
                    for item in claims[prop]
                    if 'datavalue' in item['mainsnak']  # Check for 'datavalue' key
                ]
                extracted_data[label] = [get_label_for_id(q_id) for q_id in ids]
    
    return extracted_data


def get_venice_related_entities(entity_name):
    """
    Main pipeline to search for an entity, verify if it's related to Venice, 
    and fetch relevant properties.
    """
    # Step 1: Search for the entity and get its ID(s)
    entity_id = search_entity_id(entity_name)
    if not entity_id:
        # print(f"No entity found for '{entity_name}'")
        return None

    venice_keywords = ["venice", "venetian", "venezia"]
    related_entities = []

    # for entity_id in entity_ids:
    # Step 2: Retrieve data for the found entity ID
    entity_data = get_entity_data(entity_id)

    if ("italy"or"italia"or"italian") in entity_name.lower():
        return None
    # Step 3: Check if any of the properties or descriptions contain Venice-related keywords
    is_in_venice = any(
        any(venice_keyword in str(value).lower() for venice_keyword in venice_keywords)
        for key, values in entity_data.items()
        for value in (values if isinstance(values, list) else [values])
    )
    # print(is_in_venice)

    # Check the description too
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&props=descriptions&languages=en&format=json"
    response = requests.get(url)
    data = response.json()
    description = data['entities'][entity_id].get('descriptions', {}).get('en', {}).get('value', "")
    # Expand the check to include descriptions as well
    is_in_venice = is_in_venice or any(keyword in description.lower() for keyword in venice_keywords)
    # Step 4: If related to Venice, add to the list of related entities
    if is_in_venice:
        related_entities.append(entity_data)

    # Consolidate the properties into one entry
    consolidated_data = {
        'Location': [],
        'Administrative Entity': [],
        'Coordinates': [],
        'Country': [],
        'Locale': [],
        'Metropolitan City': [],
        'Capital': []
    }

    for entity in related_entities:
        for key, value in entity.items():
            if isinstance(value, list):
                consolidated_data[key].extend(v for v in value if v not in consolidated_data[key])
            else:
                if value not in consolidated_data[key]:
                    consolidated_data[key].append(value)

    # Filter out empty values
    filtered_data = {key: value for key, value in consolidated_data.items() if value}

    return filtered_data

# place = "Venice" # 3 pass
# place = "Murano" # 3 pass
# place = "San Francesco della Vigna" # 3 pass
# place = "Giudecca" # 3 pass
# place = "Rialto Bridge" # 1 fail: wikidata
# # place = "Noale" # 2 fail: wikidata, geodata
# entity_name = "italia"
# entity_info = get_venice_related_entities(entity_name)
# print("Filtered Related Entity Information:", entity_info)

def wikidata_is_in_venice(location_name):
    location_name=location_name.lower()
    # Call get_wikidata_info and format the output
    if(location_name!="italia" and location_name!="italy" and location_name!="italu"
       and location_name!="venezia" and location_name!="venice" and location_name!="veneto" and location_name!="veneziano"):
        info = get_venice_related_entities(location_name)
        if info:
            # Return all entities that might be in Venice, with coordinates if available
            # return info
            return info['Coordinates'][0]
    else:
        return None
    

# print(wikidata_is_in_venice("haa"))
def show_all_the_ID (entity_name):
    search_url = "https://www.wikidata.org/w/api.php"
    search_params = {
        "action": "wbsearchentities",
        "search": entity_name,
        "language": "en",
        "format": "json"
    }
    
    response = requests.get(search_url, params=search_params)
    results = response.json().get('search', [])
    
    # Display search results for validation
    # print("Search results for verification:")
    entity_ids = []
    for result in results:
        # print(f"ID: {result['id']}, Label: {result['label']}, Description: {result.get('description', 'No description')}")
        entity_ids.append(result['id'])

# print(wikidata_is_in_venice("Murano"))
