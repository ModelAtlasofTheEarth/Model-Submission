import requests
import string
import json
import random
from config import MATE_DOI, NCI_RECORD
import re


def recursively_filter_key(obj, entity_template):

    """
    Recursively filters keys in a nested data structure (dictionaries, lists, tuples)
    based on a specified entity template. The function retains keys in each dictionary
    that match a set of allowed keys defined for the dictionary's '@type' in the entity
    template. Other keys are removed.

    Parameters:
    obj (dict | list | tuple): The nested data structure to be filtered. It can be a
                               dictionary, a list, a tuple, or a combination of these.
    entity_template (dict): A dictionary defining which keys to retain for each '@type'
                            in the nested dictionaries. The keys in this dictionary are
                            '@type' values, and the values are lists of keys to retain
                            in the dictionaries that have the corresponding '@type'.

    Returns:
    None: The function modifies the input object (obj) in place and does not return a value.


    Note:
    The function modifies the 'obj' argument in place. After execution, 'obj' will only
    contain the keys allowed by the 'entity_template' for each dictionary's '@type'.
    Elements of lists and tuples within 'obj' are also recursively filtered.
    """

    if isinstance(obj, dict):
        if '@type' in obj.keys():
            if obj['@type'] in entity_template.keys():
                #these are the keys we want to filter on
                type_keys = entity_template[obj['@type']]
                [obj.pop(k) for k in list(obj.keys()) if k not in type_keys]

            pass
        for key, value in obj.items():
            recursively_filter_key(value, entity_template)

    # If it's a list or a tuple, iterate over its elements
    elif isinstance(obj, (list, tuple)):
        for index, value in enumerate(obj):
            recursively_filter_key(value, entity_template)



def get_random_string(length=9):
    """
    Generates a random string of characters, with a hash prepended,
    """
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    result_str = '#' + result_str
    return result_str


def check_for_id(json_dict):
    """
    Checks if the @id key exists in a json_dict (a Python dictionary)
    """
    if '@id' in json_dict.keys():
        return True
    else:
        return False


def top_level_id(crate):

    """
    Gets a list of @id values for the top level of teh @graph array
    """
    id_list = []
    for json_dict in crate['@graph']:
        id_list.append(json_dict['@id'])

    return id_list

def is_array(var):
    return isinstance(var, (list, tuple))

def replace_blank_null_id(entity):

    """
    Fills blank '@id' key in an RO-Crate entity dictionary.

    This function examines an RO-Crate entity, represented as a dictionary,
    for the presence and value of the '@id' key.
    If '@id' is absent or its value is None, the function assigns a new value to '@id'.
    The new value is determined in the following order of preference:

    1. If 'uri' key exists in the entity, its value is used.
    2. If 'url' key exists, its value is used.
    3. If neither 'uri' nor 'url' is present, a randomly generated string is assigned.

    Args:
        entity (dict): The dictionary representing an RO-Crate entity.

    Returns:
        dict: The modified entity dictionary with an updated '@id' value.

    Note:
        The function modifies the 'entity' dictionary in-place and also returns it.
    """
    replace_string = get_random_string()

    if 'uri' in entity.keys():
        replace_string =entity['uri']
    if 'url' in entity.keys():
        replace_string =entity['url']

    #print(entity)

    #if not @id is no present or or is None, make new_id.
    if '@id' not in entity.keys():
        entity.update({'@id': replace_string })
    if '@id' in entity.keys() is True and entity['@id'] is None:
        entity.update({'@id': replace_string })

    #return entity

def search_replace_blank_node_ids(crate, graph_index):

    """
    This function retrieves a node (entity dictionary) from the '@graph' array of a
    given RO-Crate object (represented as a python dictionary) using the provided graph_index.
    It iterates through the values in the entity dictionary.
    If any of these values are nested json entities (i.e dictionaries),
    the function verifies whether these nested entities have an '@id' key.
    If an '@id' key is missing or blank for a nested entity,
    the function generates and assigns a random '@id' to that entity.

    Args:
        ro_crate (dict): The RO-Crate object, represented as a python dictionary.
        graph_index (int): The index of the entity in the '@graph' array to be extracted.

    Returns:
        None: The function modifies the ro_crate object in-place by adding '@id's to nested entities if required.
    """

    #grab the entity out of the crate as a dictionary
    json_dict = crate['@graph'][graph_index]
    #print(json_dict)
    #print(json_dict.keys())
    for key in json_dict.keys():
        entity = json_dict[key]
        #print(entity)
        if isinstance(entity, dict):
            #print(entity)
            #this should replace in place!
            replace_blank_null_id(entity)
            crate['@graph'][graph_index][key] = entity


def search_replace_sub_dict(crate, graph_index):

    """
    Extracts a nested entity from within an RO-Crate's entity and relocates it to the top level of the
    '@graph' array. This makes the json flattened and compacted.

    This function takes an RO-Crate object and a specified index,
    retrieves an entity dictionary (a node in the '@graph' array), and iterates through its values.
    If it finds any nested entities within this dictionary, it extracts these entities
    and places them at the top level of the '@graph' array. The original position of the nested entity
    within the parent entity is then replaced with the nested entity's '@id'.


    Args:
        ro_crate (dict): The RO-Crate object, represented as a python dictionary.
        graph_index (int): The index of the entity in the '@graph' array to be examined for nested entities.

    Returns:
        None: The function modifies the ro_crate object in-place, relocating nested entities and updating references.
    """


    #grab the entity out of the crate as a dictionary
    json_dict = crate['@graph'][graph_index]

    for key in json_dict.keys():


        current_ids = top_level_id(crate)
        if isinstance(json_dict[key], dict):
            try:
                at_id = json_dict[key]['@id']
            except:
                replace_blank_null_id(json_dict[key])
                at_id = json_dict[key]['@id']
            if len(json_dict[key].keys()) > 1:
                if at_id not in current_ids:
                    #dict() is necessary to make a copy not a reference
                    crate['@graph'].append(dict(json_dict[key]))

                #replace local dict with @id
                [json_dict[key].pop(k) for k in list(json_dict[key].keys()) if k != '@id']

        #recurse through any lists or tuples and check if they contain sub dictionaries.
        #a true recursive approach is not used here due to difficulties with how the function needs
        #to modfy both the ro-crate and the entity


        elif is_array(json_dict[key]):
            for j in range(len(json_dict[key])):
                #print(key, j)
                if isinstance(json_dict[key][j], dict):
                    try:
                        at_id = json_dict[key][j]['@id']
                    except:
                        replace_blank_null_id(json_dict[key][j])
                        at_id = json_dict[key][j]['@id']
                    if len(json_dict[key][j].keys()) > 1:
                        if at_id not in current_ids:
                            #the dict() is necessary to make a copy not a reference
                            crate['@graph'].append(dict(json_dict[key][j]))
                    #replace local dict with @id
                    [json_dict[key][j].pop(k) for k in list(json_dict[key][j].keys()) if k != '@id']

        else:
            pass




def apply_entity_mapping(metadata, mapping, issue_dict, graph_index):
    """
    Updates a specific entity within the metadata's @graph array using values from an issue dictionary,
    based on a provided mapping. This function iterates over the mapping dictionary, where each key-value
    pair represents a target entity attribute and its corresponding attribute in the issue dictionary.
    If the value in the mapping is a list, it collects corresponding values from the issue_dict and
    updates the target entity's attribute with this list of values. If a mapping value is None, a list with None elements,
    or a key does not exist in the issue dictionary, the corresponding attribute in the target entity is left unchanged.

    Parameters:
    - metadata (dict): The metadata structure containing an '@graph' key with a list of entities.
    - mapping (dict): A dictionary where each key represents an attribute in the target entity within
                      the metadata's '@graph' array, and each value corresponds to an attribute or a list of attributes
                      in the issue_dict. A value of None or a non-existent key results in no update for that attribute.
    - issue_dict (dict): A dictionary containing data that should be mapped to the target entity in the
                         metadata's '@graph' array.
    - graph_index (int): The index of the target entity within the metadata's '@graph' array to which the
                         mapping should be applied.

    Returns:
    None: The function updates the metadata in place and does not return a value.
    """

    # Validate metadata structure and graph_index
    if '@graph' not in metadata or not isinstance(metadata['@graph'], list):
        print("Warning: The provided metadata must contain an '@graph' key with a list of entities.")
        return
    if graph_index >= len(metadata['@graph']):
        print(f"Warning: graph_index {graph_index} is out of range for the metadata's '@graph' array.")
        return

    # Iterate over the mapping and apply updates where possible
    for target_key, issue_keys in mapping.items():
        if issue_keys is None:
            # Skip mapping if issue_keys is None
            continue

        if isinstance(issue_keys, list):
            # Handle list of keys - collect corresponding values from issue_dict
            values = [issue_dict[key] for key in issue_keys if key in issue_dict]
            if values:
                metadata['@graph'][graph_index][target_key] = values
        else:
            # Single key handling as before
            if issue_keys in issue_dict:
                metadata['@graph'][graph_index][target_key] = issue_dict[issue_keys]


def apply_entity_mapping_extended(metadata, mapping, issue_dict, graph_index):
    """
    Updates a specific entity within the metadata's @graph array using values from an issue dictionary,
    based on a provided mapping. Supports nested mappings using dot notation (e.g., "Bkey1.Bkey2" for nested items).

    Parameters:
    - metadata (dict): The metadata structure containing an '@graph' key with a list of entities.
    - mapping (dict): A dictionary where each key represents an attribute in the target entity within
                      the metadata's '@graph' array, and each value corresponds to an attribute or a list of attributes
                      in the issue_dict, supporting nested access via dot notation.
    - issue_dict (dict): A dictionary containing data that should be mapped to the target entity in the
                         metadata's '@graph' array.
    - graph_index (int): The index of the target entity within the metadata's '@graph' array to which the
                         mapping should be applied.

    Returns:
    None: The function updates the metadata in place and does not return a value.
    """

    def get_nested_value(d, key):
        """Accesses a nested value in a dictionary using a dot-separated key."""
        keys = key.split('.')
        for k in keys:
            d = d.get(k, {})
        return d if d else None

    # Validate metadata structure and graph_index
    if '@graph' not in metadata or not isinstance(metadata['@graph'], list):
        print("Warning: The provided metadata must contain an '@graph' key with a list of entities.")
        return
    if graph_index >= len(metadata['@graph']):
        print(f"Warning: graph_index {graph_index} is out of range for the metadata's '@graph' array.")
        return

    # Iterate over the mapping and apply updates where possible
    for target_key, issue_keys in mapping.items():
        if issue_keys is None:
            # Skip mapping if issue_keys is None
            continue

        if isinstance(issue_keys, list):
            # Handle list of keys - collect corresponding values from issue_dict, supporting nested keys
            values = [get_nested_value(issue_dict, key) for key in issue_keys if get_nested_value(issue_dict, key) is not None]
            if values:
                metadata['@graph'][graph_index][target_key] = values
        else:
            # Handle single or nested key
            value = get_nested_value(issue_dict, issue_keys)
            if value is not None:
                metadata['@graph'][graph_index][target_key] = value




def dict_to_ro_crate_mapping(crate, issue_dict,  mapping_list):

    """
    This function apply a mapping between a dictionary that captures key model submission data
    and a list of dictionaries, one for each of the default entities in an RO-Crate
    (as defined at https://github.com/ModelAtlasofTheEarth/metadata_schema/blob/main/README.md)
    The value of the @id provides the link the entity in the RO-crate, and the item in the mapping list.

    Parameters:

    crate: ro_crate as Python dictionary
    issue_dict: the dictionary produced by parse_issue.py
    mapping_list: a list of dictionaries that define mappings between issue_dict and
    entities in the crate


    Returns:
    None: Changes to crate occur in-place

    """


    ####################
    ##Apply mapping
    ####################

    #loop through the dictionaries in the mappign list
    #each provides a mapping between the issue_dict and a particular entitity in the R0-crate
    for i, mapping in enumerate(mapping_list):
        if '@id' in mapping.keys():
            #get the value corresponding to the @id key
            entity_val = mapping['@id']
            #now search the correspoding entity by looping through the entities in the RO-Crate @graph array
            for j, entity in enumerate(crate['@graph']):
                if entity['@id'] == entity_val:
                    #once found apply the mapping
                    apply_entity_mapping_extended(crate, mapping, issue_dict, graph_index=j)
        else:
            pass



def load_crate_template(metadata_template_url="https://raw.githubusercontent.com/ModelAtlasofTheEarth/metadata_schema/main/mate_ro_crate/ro-crate-metadata.json"):

    """
    Downloads the M@TE RO-Crate metadata template from a specified URL and returns it as a dictionary.

    Parameters:
    - metadata_template_url (str): URL to the JSON-LD metadata template.

    Returns:
    - dict: The loaded metadata template as a dictionary, or None if an error occurs.
    """

    try:
        response = requests.get(metadata_template_url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        crate = json.loads(response.text)
        print("JSON-LD data loaded successfully.")
        return crate
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the file. Error: {e}")
        return None



def load_entity_template(entity_template_url="https://raw.githubusercontent.com/ModelAtlasofTheEarth/metadata_schema/main/mate_ro_crate/type_templates.json"):
    """
    Downloads a JSON-LD entity template from the specified URL and returns it as a dictionary.

    Parameters:
    - entity_template_url (str): URL to the JSON-LD entity template.

    Returns:
    - dict: The loaded entity template as a dictionary, or None if an error occurs.
    """

    try:
        response = requests.get(entity_template_url)
        response.raise_for_status()  # Raises an HTTPError for bad HTTP responses
        entity_template = json.loads(response.text)
        print("JSON-LD data loaded successfully.")
        return entity_template
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the file. Error: {e}")
        return None


def get_next_id(existing_ids):
    """
    Generates the next unique ID based on the highest existing ID found.
    """
    if not existing_ids:
        return '#b1'  # Start from 1 if no IDs found yet
    max_id = max(existing_ids)
    next_id = max_id + 1
    return f'#b{next_id}'

def update_ids(entity, pattern, existing_ids):
    """
    Recursively updates '@id' fields in an entity if they are not valid or missing,
    ensuring not to overwrite valid existing '@id' values and generating unique IDs.
    """
    if isinstance(entity, dict):
        # If '@id' exists, check if it's valid
        if '@id' in entity:
            if isinstance(entity['@id'], str) and pattern.match(entity['@id']):
                # Extract number from existing valid ID and update the set of IDs
                num = int(pattern.findall(entity['@id'])[0])
                existing_ids.add(num)
            elif not entity['@id']:  # Check if @id is empty
                # Assign a new unique ID
                new_id = get_next_id(existing_ids)
                entity['@id'] = new_id
                existing_ids.add(int(pattern.findall(new_id)[0]))
        else:
            # No '@id' field present, create a new one
            new_id = get_next_id(existing_ids)
            entity['@id'] = new_id
            existing_ids.add(int(pattern.findall(new_id)[0]))

        # Recursively process other dictionary values
        for key, value in entity.items():
            update_ids(value, pattern, existing_ids)

    elif isinstance(entity, list):
        # Process each item in the list recursively
        for item in entity:
            update_ids(item, pattern, existing_ids)

def update_blank_node_ids(ro_crate):
    """
    Traverse the '@graph' in an RO-Crate JSON-LD document and recursively update blank node IDs,
    respecting existing valid '@id' and ensuring no duplicates.
    """
    if '@graph' not in ro_crate:
        return ro_crate

    pattern = re.compile(r'^#b(\d+)$')
    existing_ids = set()

    # First collect all valid existing IDs
    for entity in ro_crate['@graph']:
        update_ids(entity, pattern, existing_ids)

    # Reset existing IDs to handle updates properly
    existing_ids.clear()

    # Now update invalid or missing IDs
    for entity in ro_crate['@graph']:
        update_ids(entity, pattern, existing_ids)

    return ro_crate



def flatten_crate(crate):
    """
    Flattens a given RO-Crate by processing its '@graph' attribute. It iteratively applies two functions to each
    entity within the '@graph':

    1. `search_replace_blank_node_ids()`: Assigns IDs to entities that lack them.
    2. `search_replace_sub_dict()`: Moves nested dictionaries to the top level of the '@graph' and replaces
       the original nested dictionaries with references to their new top-level '@id'.

    The process repeats until the length of the '@graph' array stabilizes, indicating that all nested entities
    have been processed, resulting in a flattened and compacted crate structure.

    Parameters:
    - crate (dict): The RO-Crate object to be flattened, expected to have an '@graph' key containing a list of entities.


    Returns:
    - dict: The flattened RO-Crate with nested entities processed and moved to the top level of the '@graph'.

    Note:
    This function assumes the presence of 'search_replace_blank_node_ids' and 'search_replace_sub_dict' functions
    which are applied to each entity. It does not perform any validation on the input crate structure.
    """

    #should make this in-place, like most of the other functions
    crate = update_blank_node_ids(crate)

    try:
        current_length = len(crate['@graph'])
        previous_length = current_length - 1

        # Loop until the number of nodes in '@graph' stabilizes, indicating no more nested entities are found
        while current_length > previous_length:
            previous_length = current_length  # Update the length for comparison in the next iteration

            for i in range(current_length):
                # Apply the two functions to each entity in the '@graph'
                #search_replace_blank_node_ids(crate, i)
                search_replace_sub_dict(crate, i)

            # Update the current length after modifications
            current_length = len(crate['@graph'])


    except KeyError as e:
        # Handle cases where the expected keys are missing in the input crate
        print(f"Key error: {e}. The input crate might be missing required keys or has an incorrect structure.")
    except TypeError as e:
        # Handle cases where the input is not structured as expected (e.g., 'crate' is not a dict)
        print(f"Type error: {e}. Please ensure the input crate is a properly structured dictionary.")


def find_index_by_id(ro_crate, id_value):
    list_of_dicts = ro_crate['@graph']
    # Check if the first parameter is a list
    if not isinstance(list_of_dicts, list):
        return "Error: The first parameter must be a list of dictionaries."

    # Check if the list contains dictionaries
    for item in list_of_dicts:
        if not isinstance(item, dict):
            return "Error: All items in the list must be dictionaries."

    for index, dictionary in enumerate(list_of_dicts):
        # Check if '@id' key exists in the dictionary
        if '@id' in dictionary:
            if dictionary['@id'] == id_value:
                return index
        else:
            return "Error: One or more dictionaries in the list do not contain an '@id' key."

    # If the loop completes without returning, the id_value was not found
    return f"Warning: No dictionary found with '@id' value '{id_value}'."



def extract_project_description(owner, repo):
    """
    Download the README.md file from a GitHub repository and extract the text under the 'Project Description' heading.

    Parameters:
    owner (str): The GitHub username or organization that owns the repository.
    repo (str): The name of the repository.

    Returns:
    str: The extracted text under the 'Project Description' heading, or an error message if not found.
    """
    # Construct the URL for the raw README.md file
    url = f'https://raw.githubusercontent.com/{owner}/{repo}/main/README.md'

    # Send a GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        # If the request is successful, find the section under 'Project Description'
        content = response.text
        pattern = r'(?<=## Project Description\n)(.*?)(?=\n## |\Z)'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # If the pattern is found, return the matched text
            return match.group(0).strip()
        else:
            return "The 'Project Description' section was not found in the README.md file."
    else:
        # If the request is not successful, return an error message
        return f"Failed to download README.md: HTTP {response.status_code}"



def defaults_and_customise_ro_crate(issue_dict, ro_crate, timestamp=False):

    """
    Apply any defaults and or customising of the crate based on user input. There is some crossover here with parse_issue, which also applies some default fields
    In some cases it may be easier to apply these here. Examples are the isPartOf of puiblisher fields
    """

    #publisher default to NCI?
    #isPartOf should default to M@TE collection
    root_index = find_index_by_id(ro_crate, './')
    ro_crate['@graph'][root_index]['isPartOf'].append(MATE_DOI)
    nci_record = {'@type': 'Organization',
                 '@id': 'https://ror.org/04yx6dh41',
                 'name': 'National Computational Infrastructure'}
    ro_crate['@graph'][root_index]['publisher'] = NCI_RECORD

    #add date time as the date published ro-crate

    if timestamp:
        ro_crate['@graph'][root_index]["datePublished"] = timestamp

    #add any custom text, such as ["model_setup_description"]


    #add the project Description
    proj_description = extract_project_description("ModelAtlasofTheEarth", "metadata_schema")
    ro_crate['@graph'][root_index]["description"] = proj_description

    #resolve any potential issues with authorship and contribution

    pass
