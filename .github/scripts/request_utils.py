import requests
import os

# Base URLs configuration
BASE_URLS = {
    "publication": os.getenv("BASE_URL_PUBLICATION", "https://api.crossref.org/works/"),
    "software": os.getenv("BASE_URL_SOFTWARE", "https://doi.org/"),
    "organization": os.getenv("BASE_URL_ORGANIZATION", "https://api.ror.org/organizations/"),
    "author": os.getenv("BASE_URL_AUTHOR", "https://pub.orcid.org/v3.0/")
}


# Default timeout
TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", 10))

# Initialize a requests session
session = requests.Session()

def get_record(record_type, record_id):
    log = ""
    metadata = {}

    if record_type not in BASE_URLS:
        raise ValueError(f"Record type `{record_type}` not supported")

    # Define content types to try
    content_types = ["application/ld+json", "application/json"]

    # Iterate over URLs and content types to fetch the record
    #for url in urls:

    url = BASE_URLS[record_type] + record_id
    print(url)

    for content_type in content_types:
        headers = {"Content-Type": content_type, "Accept": content_type}

        try:
            response = session.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # If the response is successful and contains content, parse and return the metadata
            if response.content:
                metadata = response.json()
                return metadata, log  # Successful fetch, return immediately

        except requests.exceptions.RequestException as e:
            log += f"Error fetching metadata with {content_type} from {url}: {e}\n"
            # Continue to the next URL or content type

    # If metadata is still empty after all attempts, log an error
    if not metadata:
        log += "Failed to fetch metadata with any content type or URL.\n"

    return metadata, log

def search_organization(org_url):
    log = ""
    ror_id = ""
    result = {}

    base_url = "https://api.ror.org/organizations"
    org_url = org_url.split("://")[-1]

    #Check if last character is a '/' and if so drop it
    if org_url[-1] == "/": org_url = org_url[:-1]

    url = base_url + '?query.advanced=links:' + org_url
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        result = response.json()

    except requests.exceptions.RequestException as e:
        log += f"Error fetching metadata: {e} \n"

    # Deal with response and determine ROR ID
    if result["number_of_results"] == 0:
        log += f"Unable to find ROR for {org_url} \n"
    elif result["number_of_results"] == 1:
        ror_id = result["items"][0]["id"]
        log += f"Found ROR record for {org_url}: {result['items'][0]['name']} ({ror_id}) \n"
        for relation in result["items"][0]["relationships"]:
            if relation["type"] == "Parent":
                log += f"Note: This organization has a parent organization: {relation['label']} ({relation['id']}) \n"
    else:
        ror_id = result["items"][0]["id"]
        log += f"Found more than one ROR record for {org_url}. Assuming the first result is correct; if not please enter the correct ROR. \n"
        for record in result["items"]:
            log += f"\t - {record['name']} ({record['id']}) \n"

    return ror_id, log


def check_uri(uri):
    try:
        response = requests.get(uri)
        response.raise_for_status()  # Raise an exception for HTTP errors

        return "OK"

    except Exception as err:
        return err.args[0]
