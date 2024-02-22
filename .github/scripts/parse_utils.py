import os
import re
import requests
import filetype
import subprocess
from filetypes import Svg

#from improved_request_utils import get_record, search_organization
from request_utils import get_record, search_organization
from parse_metadata_utils import parse_author, parse_organization

def validate_slug(proposed_slug):
    error_log = ""

    try:
        slug_bits = proposed_slug.split("-")
        assert len(slug_bits) == 3, "Warning: slug should be in the format `familyname-year-keyword`\n"
        assert len(slug_bits[1]) == 4, "Warning: year should be in the format `yyyy`\n"
        int(slug_bits[1])
    except ValueError:
        error_log += "Warning: slug should be in the format `familyname-year-keyword` where year is a number in the format `yyyy`\n"
    except AssertionError as err:
        error_log += f"{err}\n"

    cmd = "python3 .github/scripts/generate_identifier.py"

    try:
        slug = subprocess.check_output(cmd, shell=True, text=True, stderr=open(os.devnull)).strip()
        if proposed_slug != slug:
            error_log += f"Warning: Model repo cannot be created with proposed slug `{proposed_slug}`. \n"
            error_log += f"Either propose a new slug or repo will be created with name `{slug}`. \n"
    except Exception as err:
        slug = ""
        error_log += "Error: Unable to create valid repo name... \n"
        error_log += f"`{err}`\n"

    return slug, error_log


def parse_name_or_orcid(name_or_orcid):
    error_log = ""

    if is_orcid_format(name_or_orcid):
        orcid_record, log1 = get_record("author", name_or_orcid)
        author_record, log2 = parse_author(orcid_record)
        if log1 or log2:
            error_log += log1 + log2
    else:
        try:
            familyName, givenName = name_or_orcid.split(",")
            author_record = {
                "@type": "Person",
                "givenName": givenName,
                "familyName": familyName,
            }
        except:
            error_log += f"- Error: name `{name_or_orcid}` in unexpected format. Expected `last name(s), first name(s)` or ORCID. \n"
            author_record = {}

    return author_record, error_log

def parse_yes_no_choice(input):
    if "X" in input:
        return True
    else:
        return False

def is_orcid_format(author):

    orcid_pattern = re.compile(r'\d{4}-\d{4}-\d{4}-\d{3}[0-9X]')

    if orcid_pattern.fullmatch(author):
        return True
    else:
        return False


def get_authors(author_list):
    '''
    Parses a list of author names or ORCID iDs and returns a list of dictionaries of schema.org Person type

        Parameters:
            author_list (list of strings): list of names in format Last Name(s), First Name(s) and/or ORCID iDs

        Returns:
            authors (list of dicts)
            log (string)

    '''

    log = ""
    authors = []

    for author in author_list:
        author_record, error_log = parse_name_or_orcid(author)
        if author_record:
            authors.append(author_record)
        if error_log:
            log += error_log

    return authors, log


def get_funders(funder_list):

    log = ""
    funders = []

    for funder in funder_list:
        if "ror.org" not in funder:
            ror_id, get_log = search_organization(funder)
            log += get_log

            if not ror_id:
                funders.append({"@type": "Organization", "name": funder, "url": funder})
            else:
                funder = ror_id

        if "ror.org" in funder:
            record, get_log = get_record("organization", funder)
            funder_record, parse_log = parse_organization(record)
            if get_log or parse_log:
                log += get_log + parse_log
            else:
                funders.append(funder_record)

    return funders, log


def parse_image_and_caption(img_string, default_filename):
    log = ""
    image_record = {}

    md_regex = r"\[(?P<filename>.*?)\]\((?P<url>.*?)\)"
    html_regex = r'alt="(?P<filename>[^"]+)" src="(?P<url>[^"]+)"'

    # Hack to recognise SVG files
    filetype.add_type(Svg())

    caption = []

    for string in img_string.split("\r\n"):
        if "https://" in string:
            try:
                image_record = re.search(md_regex, string).groupdict()
            except:
                if string.startswith("https://"):
                    image_record = {"filename": default_filename, "url": string}
                elif "src" in string:
                    image_record = re.search(html_regex, string).groupdict()
                else:
                    log += "Error: Could not parse image file and caption\n"
        else:
            caption.append(string)

    # Get correct file extension for images
    if "url" in image_record:
        response = requests.get(image_record["url"])
        content_type = response.headers.get("Content-Type")[:5]
        if content_type in ["video", "image"]:
            image_record["filename"] += "." + filetype.get_type(mime=response.headers.get("Content-Type")).extension

    image_record["caption"] = "\n".join(caption)

    if not caption:
        log += "Error: No caption found for image.\n"

    return image_record, log


def extract_doi_parts(doi_string):
    # Regular expression to match a DOI within a string or URL
    # It looks for a string starting with '10.' followed by any non-whitespace characters
    # and optionally includes common URL prefixes
    # the DOI
    doi_pattern = re.compile(r'(10\.[0-9]+/[^ \s]+)')

    # Search for DOI pattern in the input string
    match = doi_pattern.search(doi_string)

    # If a DOI is found in the string
    if match:
        # Extract the DOI
        doi = match.group(1)

        # Clean up the DOI by removing any trailing characters that are not part of a standard DOI
        # This includes common punctuation and whitespace that might be accidentally included
        #doi = re.sub(r'[\s,.:;]+$', '', doi)
        doi = re.sub(r'[\s,.:;|\/\?:@&=+\$,]+$', '', doi)

        # Split the DOI into prefix and suffix at the first "/"
        #prefix, suffix = doi.split('/', 1)

        return doi
    else:
        # Return an error message if no DOI is found
        return "No valid DOI found in the input string."


def extract_orcid(input_str):
    """
    Extracts an ORCiD ID from a given string.

    The function accepts a string that can either be a direct ORCiD ID or an ORCiD URL.
    It attempts to extract the ORCiD ID using a regular expression that matches both formats.
    If a valid ORCiD ID is found, it is returned. If no valid ID is found, the function returns None.

    Parameters:
    - input_str (str): A string containing a potential ORCiD ID or ORCiD URL.

    Returns:
    - str: The extracted ORCiD ID if found, otherwise None.

    Raises:
    - None: The function does not explicitly raise any errors but returns None for invalid inputs.

    Example usage:
    >>> extract_orcid("http://orcid.org/0000-0003-2198-9172")
    '0000-0003-2198-9172'

    >>> extract_orcid("0000-0002-1825-0097")
    '0000-0002-1825-0097'

    >>> extract_orcid("John Doe")  # Invalid input
    None
    """
    orcid_pattern = re.compile(r'(?:https?://orcid\.org/)?([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])')

    # Search for the pattern in the input string
    match = orcid_pattern.search(input_str)

    # If a match is found, return the ORCiD ID
    if match:
        return match.group(1)
    else:
        # If no match is found, return None
        return None



def is_orcid(input_str):
    """
    Checks if the given string matches the ORCiD pattern.

    Parameters:
    - input_str (str): A string to be checked against the ORCiD pattern.

    Returns:
    - bool: True if the string matches the ORCiD pattern, False otherwise.
    """
    orcid_pattern = re.compile(r'(?:https?://orcid\.org/)?([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])')
    return bool(orcid_pattern.match(input_str))

def remove_duplicates(list_a, list_b):
    """
    Removes items from list_b that have an @id matching any @id in list_a. If an @id is an ORCiD pattern,
    it is first normalized using extract_orcid. Otherwise, the @id is used as is.

    Parameters:
    - list_a (list): List of dictionaries potentially containing ORCiD IDs in their '@id' keys.
    - list_b (list): List of dictionaries from which items should be removed if their '@id' matches any in list_a.

    Returns:
    - list: A new list derived from list_b with items removed that have matching @id keys in list_a.
    """
    # Normalize and collect @id values from list_a
    a_ids = set()
    for item in list_a:
        if '@id' in item:
            id_val = item['@id']
            if is_orcid(id_val):
                a_ids.add(extract_orcid(id_val))
            else:
                a_ids.add(id_val)

    # Filter list_b based on @id values found in a_ids
    filtered_b_list = []
    for item in list_b:
        if '@id' in item:
            id_val = item['@id']
            normalized_id = extract_orcid(id_val) if is_orcid(id_val) else id_val
            if normalized_id not in a_ids:
                filtered_b_list.append(item)

    return filtered_b_list
