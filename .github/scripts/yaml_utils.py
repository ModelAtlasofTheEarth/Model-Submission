import re
import copy
from ruamel.yaml import YAML
import io
from config import *


def navigate_and_assign(source, path, value):
    """Navigate through a nested dictionary and assign a value to the specified path."""
    keys = path.split('.')
    for i, key in enumerate(keys[:-1]):
        if key.isdigit():  # If the key is a digit, it's an index for a list
            key = int(key)
            while len(source) <= key:  # Extend the list if necessary
                source.append({})
            source = source[key]
        else:
            if i < len(keys) - 2 and keys[i + 1].isdigit():  # Next key is a digit, so ensure this key leads to a list
                source = source.setdefault(key, [])
            else:  # Otherwise, it leads to a dictionary
                source = source.setdefault(key, {})
    # Assign the value to the final key
    if keys[-1].isdigit():  # If the final key is a digit, it's an index for a list
        key = int(keys[-1])
        while len(source) <= key:  # Extend the list if necessary
            source.append(None)
        source[key] = value
    else:
        source[keys[-1]] = value

def navigate_and_retrieve(source, path):
    """Navigate through a nested structure and retrieve the value at the specified path, returning None if not found."""
    keys = path.split('.')
    for key in keys:
        try:
            if isinstance(source, dict):
                source = source[key]
            elif isinstance(source, list) and key.isdigit():
                source = source[int(key)]
        except (KeyError, IndexError):
            # Return None if the key or index is not found
            return None
    return source

def expand_mapping_for_lists(b, c_original):
    """Expand mappings to include list indices for any lists encountered in B."""
    expanded_mappings = {}

    def insert_index_in_path(path, index):
        """Insert an index into a path immediately following the list identifier."""
        parts = path.split('.')
        for i, part in enumerate(parts):
            if i < len(parts) - 1 and part.isdigit() is False and parts[i + 1].isdigit() is False:
                # Check if the current part of the path refers to a list in B
                if isinstance(get_value(b, parts[:i + 1]), list):
                    return '.'.join(parts[:i + 1] + [str(index)] + parts[i + 1:])
        return path  # Return the original path if no list is found

    for c_path, b_path in c_original.items():
        current_location = b
        for part in b_path.split('.'):
            if isinstance(current_location, list):
                # When a list is encountered, expand the mapping for each item
                for i, _ in enumerate(current_location):
                    expanded_b_path = insert_index_in_path(b_path, i)
                    expanded_c_path = insert_index_in_path(c_path, i)
                    expanded_mappings[expanded_c_path] = expanded_b_path
                break  # Stop expanding this path as we've handled the list
            else:
                current_location = current_location.get(part, {})
        else:
            # If no list is encountered, keep the original mapping
            expanded_mappings[c_path] = b_path

    return expanded_mappings

def apply_mapping(a, b, c):
    """Apply the mappings to dictionary A, printing a warning and assigning None for missing keys in B."""
    for a_path, b_path in c.items():
        value = navigate_and_retrieve(b, b_path)
        if value is None:
            #print(f"Warning: Key '{b_path}' not found in B. Assigning None to '{a_path}' in A.")
            print(f"Warning: Key '{b_path}' not found in B. Assigning empty string to '{a_path}' in A.")
            value = ''
        navigate_and_assign(a, a_path, value)

def map_dictionaries(a, b, c):
    """Map values from dictionary B to dictionary A using the mapping defined in dictionary C, dynamically handling lists."""
    expanded_c = expand_mapping_for_lists(b, c)
    apply_mapping(a, b, expanded_c)


def get_value(d, keys):
    """Get a value from a nested dictionary given a list of keys."""
    for key in keys:
        if isinstance(d, list):
            key = int(key)  # Convert key to int if we're indexing a list
        d = d[key]
    return d




def extract_orcid_id(orcid_input):
    # Convert input to string if it's not, to handle integers and other non-string inputs
    orcid_str = str(orcid_input)

    # First, try to match the standard ORCiD format with hyphens
    pattern_hyphenated = re.compile(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9X]')
    match = pattern_hyphenated.search(orcid_str)

    if match:
        # If a match is found, return the matched string (the ORCiD ID)
        return match.group()

    # If no match is found, try to match a continuous string of digits
    pattern_continuous = re.compile(r'\d{15,16}')
    match_continuous = pattern_continuous.search(orcid_str)

    if match_continuous:
        # If a match is found, format the string with hyphens and return
        digits = match_continuous.group()
        return f"{digits[:4]}-{digits[4:8]}-{digits[8:12]}-{digits[12:]}"

    # If no valid format is found, return an indication that the input is not a valid ORCiD ID
    return "Invalid ORCiD ID"


def extract_integers(input_data):
    # Initialize an empty list to hold the extracted integers
    integers = []

    # Check if the input is a single integer and directly append it to the list
    if isinstance(input_data, int):
        integers.append(input_data)
    elif isinstance(input_data, str):
        # If the input is a string, extract numbers using regular expressions
        pattern = re.compile(r'\d+')
        integers.extend([int(match) for match in pattern.findall(input_data)])
    elif isinstance(input_data, list):
        # If the input is a list, iterate through the elements
        for item in input_data:
            if isinstance(item, int):
                # Directly append integers to the list
                integers.append(item)
            elif isinstance(item, str):
                # Extract numbers from strings as before
                pattern = re.compile(r'\d+')
                integers.extend([int(match) for match in pattern.findall(item)])

    return integers

def ensure_path_starts_with_pattern(file_path, pattern='./graphics/'):
    # Check if the file path starts with the specified pattern
    if not file_path.startswith(pattern):
        # If it doesn't, prepend the pattern to the file path
        file_path = pattern + file_path

    return file_path

def configure_yaml_output_dict(output_dict, issue_dict,
                               image_path='./graphics/',
                               timestamp=False):

                               #nci_file_path_base

    #establish the slug that is beign used
    if issue_dict['slug']:
        path_slug = issue_dict['slug']
    elif issue_dict['proposed_slug']:
            path_slug = issue_dict['proposed_slug']
    else:
        path_slug = 'PENDING'

    #make some changes (in-place) to output_dict, to help wrangle the yaml output dict

    #add in defaults that aren't handled elsewhere
    #add in the template key for this page
    output_dict['templateKey'] = 'model'
    #add the licence file default name (path relative to index.md)
    output_dict['licence']['licence_file'] = 'license.txt'
    #add location of the the metadata file (path relative to index.md)
    output_dict['metadataFile'] = 'ro-crate-metadata.json'





    thredds_string = MATE_THREDDS_BASE.format(path_slug)
    ## add the NCI_file_path
    if issue_dict["include_model_output"]:
        #for now, just link both to the thredds base.
        output_dict['dataset']['nci_file_path'] = thredds_string #+ '/model_output_data'

    if issue_dict["include_model_code"]:
        output_dict['model_files']['nci_file_path'] =  thredds_string #+ '/model_code_inputs'

    #url string
    url_string = MATE_WEBSITE + '/models/{}'.format(path_slug)
    output_dict['url'] = url_string

    #change format of ORCiD ids if required
    for creator in output_dict['creators']:
        creator['ORCID'] = extract_orcid_id(creator['ORCID'])



    # Format the datetime as specified, with milliseconds set to .000
    if timestamp:
        output_dict['date'] = timestamp

    #enforce list and sytax for FOR codes
    updated_codes = extract_integers(output_dict['for_codes'])
    output_dict.update({'for_codes': updated_codes })

    #By default empty values are empty strings.
    #som items need to be empyt (i.e. None)
    if output_dict['featuredpost'] == '':
        output_dict['featuredpost'] = None
    if output_dict['status'] == '':
        output_dict['status'] = None

    #append image_path to image file names if required
    for key, im_dict in output_dict['images'].items():
        if not output_dict['images'][key]['src']:
            pass
        else:
            path = ensure_path_starts_with_pattern(output_dict['images'][key]['src'], image_path)
            output_dict['images'][key]['src'] = path

    #append image_path to animation file name if required
    if output_dict['animation']['src'] is None:
        pass
    else:
        path = ensure_path_starts_with_pattern(output_dict['animation']['src'], image_path)
        output_dict['animation']['src'] = path

    #the followign files are array types
    #for_codes, status, software, creators, associated_publication,
    #research_tags, compute_tags, funder funding, images, model_files, dataset



    #check that any structures that need to be in lists/arrays are in lists/arrays
    #mainly this is just to get the right structures out for Gatsby,
    #for instance, the concatenation for tags requires arrays - can't be strings
    #and an array with an empty string results in a empty tag (a hyphen)

    if not isinstance(output_dict['software'], list):
        if output_dict['software']:
            output_dict['software'] = [output_dict['software']]
        #return an empty list, not a list of empty string
        else:
            output_dict['software'] = []
    if not isinstance(output_dict['research_tags'], list):
            if output_dict['research_tags']:
                output_dict['research_tags'] = [output_dict['research_tags']]
            else:
                output_dict['research_tags'] = []
    if not isinstance(output_dict['compute_tags'], list):
            if output_dict['compute_tags']:
                output_dict['compute_tags'] = [output_dict['compute_tags']]
            else:
                output_dict['compute_tags'] = []


    #Add any additional mappings that we can't manage in the generalised function
    try:
        output_dict['associated_publication']['publisher']  = issue_dict['publication']['isPartOf'][0]['isPartOf']['publisher']
        output_dict['associated_publication']['journal']    = issue_dict['publication']['isPartOf'][0]['isPartOf']['name'][0]
        output_dict['associated_publication']['date']       = issue_dict['publication']['isPartOf'][0]['datePublished']
    except:
        pass



def save_yaml_with_header(yaml_content, file_path=None):

    """
    Encloses the given YAML content in YAML header delimiters '---' and saves it to the specified file path.

    :param yaml_content: A string representing the YAML content to be saved.
    :param file_path: The file path where the YAML content will be saved.
    """
    # Ensure the YAML content is enclosed with '---' delimiters
    formatted_content = f"---\n{yaml_content.strip()}\n---\n"

    if file_path is None:
        return formatted_content

    else:

        # Write the formatted content to the file
        with open(file_path, 'w') as file:
            file.write(formatted_content)
        print(f"YAML content saved to {file_path}")



def format_yaml_string(web_yaml_dict):
    yaml = YAML(typ=['rt', 'string'])
    yaml.preserve_quotes = True
    #control the indentation...
    yaml.indent(mapping=2, sequence=4, offset=2)
    # Use an in-memory text stream to hold the YAML content
    stream = io.StringIO()
    stream.write('---\n')
    yaml.dump(web_yaml_dict, stream)
    stream.write('---\n')
    yaml_content_with_frontmatter = stream.getvalue()
    return yaml_content_with_frontmatter
