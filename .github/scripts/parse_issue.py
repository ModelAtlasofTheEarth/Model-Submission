import re
import pandas as pd
from collections import defaultdict

#from improved_request_utils import get_record, check_uri
from request_utils import get_record, check_uri
from parse_metadata_utils import parse_publication, parse_software
from parse_utils import parse_name_or_orcid, parse_yes_no_choice, get_authors, get_funders, parse_image_and_caption, validate_slug, extract_doi_parts


def read_issue_body(issue_body):
    """
    Parses the markdown content of a GitHub issue body and extracts structured data.

    This function uses regular expressions to identify markdown headings (formatted as '### Heading') and the text that follows them up to the next heading or the end of the document. It constructs a dictionary where each heading is a key and the associated text is the corresponding value.

    Parameters:
    - issue_body (str): The markdown content of a GitHub issue body.

    Returns:
    - dict: A dictionary with keys derived from markdown headings and values containing the text following these headings up to the next heading or the end of the document.

    Note:
    - The function assumes that the issue body uses '###' markdown syntax for headings.
    - Headings are used as dictionary keys and should be unique within the issue body for the resulting dictionary to capture all data correctly.
    """
    regex = r"### *(?P<key>.*?)\s*[\r\n]+(?P<value>[\s\S]*?)(?=###|$)"
    data = dict(re.findall(regex, issue_body))
    return data





def parse_issue(issue):

    """
    Parses issue data to extract and structure relevant information into a dictionary format suitable for metadata representation.

    The function processes the body of an issue, extracting information based on predefined headings. It applies mappings, validations, and transformations to structure this information according to Research Object Crate (RO-Crate) metadata standards and other specified requirements. It also generates an error log capturing issues encountered during the parsing process, such as missing responses, invalid data, or errors in fetching related metadata.

    Parameters:
    - issue (object): An object representing the GitHub issue, containing at least a 'body' attribute with the issue's content.

    Processing Steps:
    1. Extract key-value pairs from the issue body using regular expressions, where keys are derived from headings and values from the subsequent text.
    2. Initialize an empty data dictionary to hold structured metadata and an error log string.
    3. For each expected piece of information (e.g., creator, slug, license), perform the following:
       - Extract and clean the relevant data from the extracted key-value pairs.
       - Validate and transform the data as necessary (e.g., checking validity of slugs, parsing DOIs, loading license information from a CSV).
       - Update the data dictionary with the structured information.
       - Log any warnings or errors encountered during processing in the error log.
    4. Return the structured metadata dictionary along with the error log.

    Returns:
    - tuple: A tuple containing two elements:
        - data_dict (dict): A dictionary containing structured metadata extracted and processed from the issue.
        - error_log (str): A string containing logged warnings and errors encountered during the parsing process.

    Note:
    - The function assumes the presence of external helper functions for specific processing steps, such as `parse_name_or_orcid`, `validate_slug`, `load_entity_template`, `recursively_filter_key`, `load_crate_template`, `dict_to_ro_crate_mapping`, `customise_ro_crate`, `flatten_crate`, `parse_publication`, `get_record`, `get_authors`, `get_funders`, `check_uri`, `parse_software`, `parse_image_and_caption`, which need to be defined elsewhere.
    - The function also relies on external resources, such as a CSV file for license information, and assumes a specific structure for the issue body based on headings and responses.
    - In general, the function steps are not order dependent. However, to work correctlly some order dependence is required. For instance, the publication record must be created before it can be used to prefil other sections.
    - For this reason, parts of the record (publication, software) that may be used in creating other items, get built first.
    """

    #read in the issue markdown as a dictionary
    data = read_issue_body(issue.body)


    error_log = ""

    # Initialize data_dict with all expected keys set to None

    #data_dict = {
    #    "creator": None,
    #    "slug": None,
    #    "for_codes": None,
    #    "license": None,
    #    "model_category": None,
    #    "publication": None,
    #    "title": None,
    #    "description": None,
    #    "authors": None,
    #    "scientific_keywords": None,
    #    "funder": None,
    #    "include_model_code": None,
    #    "model_code_inputs": None,
    #    "include_model_output": None,
    #    "model_output_data": None,
    #    "software": None,
    #    "computer_uri": None,
    #    "landing_image": None,
    #    "animation": None,
    #    "graphic_abstract": None,
    #    "model_setup_figure": None,
    #    "model_setup_description": None
    #}

    data_dict = {}

    #############
    # Fill in 'publication' record first as it may be required by other items
    #############

    # associated publication DOI
    publication_doi = data["-> associated publication DOI"].strip()
    publication_record = {}

    if publication_doi == "_No response_":
        error_log += "**Associated Publication**\n"
        error_log += "Warning: No DOI provided. \n"
    else:
        try:
            publication_metadata, log1 = get_record("publication", publication_doi)
            publication_record, log2 = parse_publication(publication_metadata)
            if log1 or log2:
                error_log += "**Associated Publication**\n" + log1 + log2
        except Exception as err:
            error_log += "**Associated Publication**\n"
            error_log += f"Error: unable to obtain metadata for DOI `{publication_doi}` \n"
            error_log += f"`{err}`\n"

    data_dict["publication"] = publication_record

    #############
    # Fill in 'software' record next as it may be required by other items
    #############
    # software framework DOI/URI
    software_doi = data["-> software framework DOI/URI"].strip()

    software_doi_only = extract_doi_parts(software_doi)

    software_record={"@type": "SoftwareApplication"}

    if software_doi == "_No response_":
        error_log += "**Software Framework DOI/URI**\n"
        error_log += "Warning: no DOI/URI provided.\n"

    else:
        try:
            software_metadata, log1 = get_record("software", software_doi_only)
            software_record, log2 = parse_software(software_metadata, software_doi)
            if log1 or log2:
                error_log += "**Software Framework DOI/URI**\n" + log1 + log2
        except Exception as err:
            error_log += "**Software Framework DOI/URI**\n"
            error_log += f"Error: unable to obtain metadata for DOI `{software_doi}` \n"
            error_log += f"`{err}`\n"
    #else:
            #error_log += "**Software Framework DOI/URI**\n Non-Zenodo software dois not yet supported\n"

    # software framework source repository
    software_repo = data["-> software framework source repository"].strip()

    if software_repo == "_No response_":
        error_log += "**Software Repository**\n"
        error_log += "Warning: no repository URL provided. \n"
    else:
        response = check_uri(software_repo)
        if response == "OK":
            software_record["codeRepository"] = software_repo
        else:
            error_log += "**Software Repository**\n" + response + "\n"

    # name of primary software framework
    software_name = data["-> name of primary software framework (e.g. Underworld, ASPECT, Badlands, OpenFOAM)"].strip()

    if software_name == "_No response_":
        try:
            software_name = software_record['name']
        except:
            error_log += "**Name of primary software framework**\n"
            error_log += "Error: no name found \n"
    else:
        software_record["name"] = software_name     # N.B. this will overwrite any name obtained from the DOI

    # software framework authors
    authors = data['-> software framework authors'].strip().split('\r\n')

    if authors[0] == "_No response_":
        try:
            software_author_list = software_record["author"]
        except:
            software_author_list = []
            error_log += "**Software framework authors**\n"
            error_log += "Error: no authors found \n"
    else:
        software_author_list, log = get_authors(authors)
        software_record["author"] = software_author_list     # N.B. this will overwrite any name obtained from the DOI
        if log:
            error_log += "**Software framework authors**\n" + log

    # software & algorithm keywords
    software_keywords = [x.strip() for x in data["-> software & algorithm keywords"].split(",")]

    if software_keywords[0] == "_No response_":
        error_log += "**Software & algorithm keywords**\n"
        error_log += "Warning: no keywords given. \n"
    else:
        software_record["keywords"] = software_keywords

    data_dict["software"] = software_record


    #############
    # Section 1
    #############
    # contributor is not necessarily the orginal creator/author of the original model
    # we use the authors field to allow attribution of the model creators
    # if the is not the origianl author, they should ensure that they are not enfriging copyright
    # cc licences will generally allow for such usage, with varying conditions.
    contributor = data["-> contributor ORCID (or name)"].strip()
    contributor_record, log = parse_name_or_orcid(contributor)
    data_dict["contributor"] = contributor_record
    if log:
        error_log += "**Contributor**\n" + log +"\n"

    # slug
    proposed_slug = data["-> slug"].strip()

    slug, log = validate_slug(proposed_slug)
    data_dict["slug"] = slug
    if log:
        error_log += "**Model Repository Slug**\n" + log + '\n'

    # FoR codes
    about_record = {
        "@id": "https://linked.data.gov.au/def/anzsrc-for/2020/370401",
        "@type": "DefinedTerm",
        "name": "Computational modelling and simulation in earth sciences",
        "termCode": "370401"
        }

    data_dict["for_codes"] = about_record

    # license
    license = data["-> license"].strip()
    license_lut = pd.read_csv(".github/scripts/licenses.csv", dtype=str)

    license_record = {}
    if license != "No license":
        license_record["name"] = license_lut[license_lut.license == license].name.values[0]
        license_record["url"] = license_lut[license_lut.license == license].url.values[0]
        license_record["text"] = license_lut[license_lut.license == license].text.values[0]
        license_record["website_path"] = license_lut[license_lut.license == license].website_path.values[0]
    else:
        license_record["name"] = "No license"
    data_dict["license"] = license_record

    # model category
    model_category = [x.strip() for x in data["-> model category"].split(",")]

    if model_category[0] == "_No response_":
        model_category = []
        error_log += "**Model category**\n"
        error_log += "Warning: No category selected \n"

    data_dict["model_category"] = model_category




    # title
    title = data["-> title"].strip()

    if title == "_No response_":
        try:
            title = publication_record['name']
        except:
            title = ""
            error_log += "**Title**\n"
            error_log += "Error: no title found \n"

    data_dict["title"] = title

    # description
    description = data["-> description"].strip()

    if description == "_No response_":
        try:
            description = publication_record['abstract']
        except:
            description = ""
            error_log += "**Description**\n"
            error_log += "Error: no descrition found, nor abstract for associated publication \n"

    data_dict["description"] = description

    # model authors
    authors = data['-> model authors'].strip().split('\r\n')

    if authors[0] == "_No response_":
        try:
            author_list = publication_record["author"]
        except:
            author_list = []
            error_log += "**Model authors**\n"
            error_log += "Error: no authors found \n"
    else:
        author_list, log = get_authors(authors)
        if log:
            error_log += "**Model authors**\n" + log

    data_dict["authors"] = author_list

    # scientific keywords
    keywords = [x.strip() for x in data["-> scientific keywords"].split(",")]

    if keywords[0] == "_No response_":
        keywords = []
        error_log += "**Scientific keywords**\n"
        error_log += "Warning: No keywords given \n"

    data_dict["scientific_keywords"] = keywords

    # funder
    funders = [x.strip() for x in data["-> funder"].split(",")]

    if funders[0] == "_No response_":
        try:
            funder_list = publication_record['funder']
        except:
            funder_list = []
            error_log += "**Funder**\n"
            error_log += "Warning: No funders provided or found in publication. \n"
    else:
        funder_list, log = get_funders(funders)
        if log:
            error_log += "**Funder**\n" + log

    data_dict["funder"] = funder_list

    #############
    # Section 2
    #############
    # include model code
    model_code = data["-> include model code ?"].strip()
    data_dict["include_model_code"] = parse_yes_no_choice(model_code)

    # model code/inputs
    model_code_record = {}
    # model code/inputs DOI
    model_code_doi = data["-> model code/inputs DOI"].strip()

    if model_code_doi == "_No response_":
        model_code_doi = ""
        error_log += "**Model code/inputs DOI**\n"
        error_log += "Warning: No DOI/URI provided. \n"
    else:
        response = check_uri(model_code_doi)
        if response != "OK":
            model_code_doi = ""
            error_log += f"**Model code/inputs DOI**\n {response} \n"

    model_code_record["doi"] = model_code_doi

    # model code/inputs notes
    model_code_notes = data["-> model code/inputs notes"].strip()

    if model_code_notes == "_No response_":
        model_code_notes = ""
        error_log += "**Model code/inputs notes**\n"
        error_log += "Warning: No notes provided.\n"

    model_code_record["notes"] = model_code_notes

    data_dict["model_code_inputs"] = model_code_record

    # include model output data
    model_output = data["-> include model output data?"].strip()
    data_dict["include_model_output"] = parse_yes_no_choice(model_output)

    # model output data
    model_output_record = {}

    # model output URI/DOI
    model_output_doi = data["-> model output data DOI"].strip()

    if model_output_doi == "_No response_":
        model_output_doi = ""
        error_log += "**Model output DOI**\n"
        error_log += "Warning: No DOI/URI provided. \n"
    else:
        response = check_uri(model_output_doi)
        if response != "OK":
            model_output_doi = ""
            error_log += "**Model output DOI**\n" + response + "\n"

    model_output_record["doi"] = model_output_doi

    # model output notes
    model_output_notes = data["-> model output data notes"].strip()

    if model_output_notes == "_No response_":
        model_output_notes = ""
        error_log += "**Model data notes**\n"
        error_log += "Warning: No notes provided.\n"

    model_output_record["notes"] = model_output_notes

    # model output size
    model_output_size = data["-> model output data size"].strip()

    if model_output_size == "_No response_":
            model_output_size = ""
            error_log += "**Model data size**\n"
            error_log += "Warning: No notes provided.\n"

    model_output_record["size"] = model_output_size

    data_dict["model_output_data"] = model_output_record


    #############
    # Section 3
    #############


    # computer URI/DOI
    computer_uri = data["-> computer URI/DOI"].strip()

    if computer_uri == "_No response_":
        error_log += "**Computer URI/DOI**\n"
        error_log += "Warning: No URI/DOI provided. \n"
    else:
        response = check_uri(computer_uri)
        if response == "OK":
            data_dict["computer_uri"] = computer_uri
        else:
            error_log += "**Computer URI/DOI**\n" + response + "\n"

    #############
    # Section 4
    #############
    # landing page image and caption
    img_string = data["-> add landing page image and caption"].strip()

    if img_string == "_No response_":
        error_log += "**Landing page image**\n"
        error_log += "Error: No image uploaded.\n\n"
    else:
        landing_image_record, log = parse_image_and_caption(img_string, "landing_image")
        if log:
            error_log += "**Landing page image**\n" + log + "\n"
        data_dict["landing_image"] = landing_image_record

    # animation
    img_string = data["-> add an animation (if relevant)"].strip()

    if img_string == "_No response_":
        error_log += "**Animation**\n"
        error_log += "Warning: No animation uploaded.\n\n"
    else:
        animation_record, log = parse_image_and_caption(img_string, "animation")
        if log:
            error_log += "**Animation**\n" + log + "\n"
        data_dict["animation"] = animation_record

    # graphic abstract
    img_string = data["-> add a graphic abstract figure (if relevant)"].strip()

    if img_string == "_No response_":
        error_log += "**Graphic abstract**\n"
        error_log += "Warning: No image uploaded.\n\n"
    else:
        graphic_abstract_record, log = parse_image_and_caption(img_string, "graphic_abstract")
        if log:
            error_log += "**Graphic abstract**\n" + log + "\n"
        data_dict["graphic_abstract"] = graphic_abstract_record

    # model setup figure
    img_string = data["-> add a model setup figure (if relevant)"].strip()

    if img_string == "_No response_":
        error_log += "**Model setup figure**\n"
        error_log += "Warning: No image uploaded.\n\n"
    else:
        model_setup_fig_record, log = parse_image_and_caption(img_string, "model_setup")
        if log:
            error_log += "**Model setup figure**\n" + log + "\n"
        data_dict["model_setup_figure"] = model_setup_fig_record

    # description
    model_description = data["-> add a description of your model setup"].strip()

    if model_description == "_No response_":
        error_log += "**Model setup description**\n"
        error_log += "Warning: No description given \n"
    else:
        data_dict["model_setup_description"] = model_description


    return data_dict, error_log
