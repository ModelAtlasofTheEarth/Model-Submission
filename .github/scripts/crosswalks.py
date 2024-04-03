import json
from ro_crate_utils import *
from crosswalk_mappings import *
from yaml_utils import *
import ruamel.yaml
import copy
from pyld import jsonld

Ryaml = ruamel.yaml.YAML(typ=['rt', 'string'])
Ryaml.preserve_quotes = True
#control the indentation...
Ryaml.indent(mapping=2, sequence=4, offset=2)



def dict_to_report(issue_dict, verbose = False):

    """
    Generates a detailed report in Markdown format based on the provided issue dictionary.The function supports a verbose mode that includes additional details such as software framework authors and a dictionary dump for testing purposes.

    Parameters:
        issue_dict (dict): A dictionary containing all the necessary information to generate the report.
        verbose (bool, optional): If True, includes additional details in the report. Default is False.

    Returns:
        str: A string containing the complete report in Markdown format.
    """

    #############
    # Section 1
    #############
    report = "## Section 1: Summary of your model   \n\n"
    # contributor
    report += "**Model Submitter:**  \n\n"
    report += f"{issue_dict['submitter']['givenName']} {issue_dict['submitter']['familyName']} "
    if "@id" in issue_dict["submitter"]:
        report += f"([{issue_dict['submitter']['@id'].split('/')[-1]}]({issue_dict['submitter']['@id']}))"

    report += "\n\n"

    # model creators(s)
    report += "**Model Creator(s):**  \n\n"
    for creator in issue_dict["creators"]:
        report += f"- {creator['givenName']} {creator['familyName']} "
        if "@id" in creator:
            report += f"([{creator['@id'].split('/')[-1]}]({creator['@id']}))"
        report += "  \n"
    report += "  \n"

    # model contributors(s)
    #report += "**Model Contributor(s):**  \n\n"
    #for contributor in issue_dict["contributors"]:
    #    report += f"- {contributor['givenName']} {contributor['familyName']} "
    #    if "@id" in contributor:
    #        report += f"([{contributor['@id'].split('/')[-1]}]({contributor['@id']}))"
    #    report += "  \n"
    #report += "  \n"



    # slug, this gets mapped to name. This is what the model is called on NCI
    report += "**Model name:**  \n\n"
    report += f"`{issue_dict['slug']}` \n\n" + "(this will be the name of the model repository when created) \n\n"


    # title. Note title doesn't appear in CreativeWorks. This gets mapped to alternateName.
    report += "**Model long name:**  \n\n"
    report += f"_{issue_dict['title']}_  \n\n"

    # license
    report += "**License:**  \n\n"
    if "url" in issue_dict["license"]:
        report += f"[{issue_dict['license']['description']}]({issue_dict['license']['url']})\n\n"
    else:
        report += f"{issue_dict['license']['description']}\n\n"

    # model category
    report += "**Model Category:**  \n\n"
    for category in issue_dict["model_category"]:
        report += f"- {category}   \n"
    report += "  \n"

    # model category
    report += "**Model Status:**  \n\n"
    for status in issue_dict["model_status"]:
        report += f"- {status}   \n"
    report += "  \n"

    # associated publication DOI
    if "@id" in issue_dict["publication"]:
        report += "**Associated Publication title:**  \n\n"
        report += f"_[{issue_dict['publication']['name']}]({issue_dict['publication']['@id']})_ \n\n"



    # abstract
    report += "**Abstract:**  \n\n"
    report += issue_dict["abstract"] + "\n\n"



    # scientific keywords
    if issue_dict["scientific_keywords"]:
        report += "**Scientific Keywords:**  \n\n"
        for keyword in issue_dict["scientific_keywords"]:
            report += f"- {keyword}   \n"
        report += "  \n"

    # funder
    report += "**Funder(s):**  \n"
    for funder in issue_dict["funder"]:
        report += f"- {funder['name']} "
        if "@id" in funder:
            report += f"({funder['@id']})"
        elif "url" in funder:
            report += f"({funder['url']})"
        report += "  \n"
    report += "  \n"


    #############
    # Section 2
    #############

    report += "## Section 2: your model code, output data  \n\n"

    # include model code
    if "embargo" in issue_dict:
        if issue_dict["embargo"][0] is True:
            report += "**Embargo on model contents requested until:**   \n\n"
            report += f"{issue_dict['embargo'][1]} \n\n"
        else:
            report +=  "** No embargo on model contents requested**"


    # include model code
    if "include_model_code" in issue_dict:
        report += "**Include model code:**   \n\n"
        report += f"{str(issue_dict['include_model_code'])} \n\n"

    # model code URI/DOI
    if issue_dict["model_code_inputs"]["doi"]:
        report += "**Model code existing URL/DOI:**   \n\n"
        report += f"{issue_dict['model_code_inputs']['doi']} \n\n"

    # model code notes
    if issue_dict["model_code_inputs"]["notes"]:
        report += "**Model code notes:**   \n\n"
        report += f"{issue_dict['model_code_inputs']['notes']} \n\n"

    # include model output data
    if "include_model_output" in issue_dict:
        report += "**Include model output data:**   \n\n"
        report += f"{str(issue_dict['include_model_output'])} \n\n"

    # model output URI/DOI
    if issue_dict["model_output_data"]["doi"]:
        report += "**Model output data, existing URL/DOI:**   \n\n"
        report += f"{issue_dict['model_output_data']['doi']} \n\n"

    # model output notes
    if issue_dict["model_output_data"]["notes"]:
        report += "**Model output data notes:**   \n\n"
        report += f"{issue_dict['model_output_data']['notes']} \n\n"


    #############
    # Section 3
    #############
    report += "## Section 3: software framework and compute details   \n"
    # software framework DOI/URI
    if "@id" in issue_dict["software"]:
        report += "**Software Framework DOI/URL:**  \n\n"
        report += f"Found software: _[{issue_dict['software']['name']}]({issue_dict['software']['@id']})_ \n\n"

    # software framework source repository
    if "codeRepository" in issue_dict["software"]:
        report += "**Software Repository:**   \n\n"
        report += f"{issue_dict['software']['codeRepository']} \n\n"

    # name of primary software framework
    if "name" in issue_dict["software"]:
        report += "**Name of primary software framework:**  \n\n"
        report += f"{issue_dict['software']['name']} \n\n"

    if verbose is True:
        #software framework authors
        if "author" in issue_dict["software"]:
            report += "**Software framework authors:**  \n"
            for author in issue_dict["software"]["author"]:
                if "givenName" in author:
                    report += f"- {author['givenName']} {author['familyName']} "
                elif "name" in author:
                    report += f"- {author['name']} "
                if "@id" in author:
                    report += f"([{author['@id'].split('/')[-1]}]({author['@id']}))"
                report += "  \n"
            report += "  \n"

    # software & algorithm keywords
    if "keywords" in issue_dict["software"]:
        report += "**Software & algorithm keywords:**  \n\n"
        for keyword in issue_dict["software"]["keywords"]:
            report += f"- {keyword}   \n"
        report += "  \n"

    # computer URI/DOI
    if "computer_uri" in issue_dict:
        report += "**Computer DOI/URL:**   \n\n"
        report += f"{issue_dict['computer_uri']} \n\n"

    #############
    # Section 4
    #############
    report += "## Section 4: web material (for mate.science)   \n"
    # landing page image and caption
    if "landing_image" in issue_dict:
        report += "**Landing page image:**  \n\n"
        if "filename" in issue_dict["landing_image"]:
            report += f"Filename: [{issue_dict['landing_image']['filename']}]({issue_dict['landing_image']['url']})  \n"
        if "caption" in issue_dict["landing_image"]:
            report += f"Caption: {issue_dict['landing_image']['caption']}  \n"
        report += '  \n'

    # animation
    if "animation" in issue_dict:
        report += "**Animation:**  \n\n"
        if "filename" in issue_dict["animation"]:
            report += f"Filename: [{issue_dict['animation']['filename']}]({issue_dict['animation']['url']})  \n"
        if "caption" in issue_dict["animation"]:
            report += f"Caption: {issue_dict['animation']['caption']}  \n"
        report += '  \n'

    # graphic abstract
    if "graphic_abstract" in issue_dict:
        report += "**Graphic abstract:**  \n\n"
        if "filename" in issue_dict["graphic_abstract"]:
            report += f"Filename: [{issue_dict['graphic_abstract']['filename']}]({issue_dict['graphic_abstract']['url']})  \n"
        if "caption" in issue_dict["graphic_abstract"]:
            report += f"Caption: {issue_dict['graphic_abstract']['caption']}  \n"
        report += '  \n'

    # model setup figure
    if "model_setup_figure" in issue_dict:
        report += "**Model setup figure:**  \n\n"
        if "filename" in issue_dict["model_setup_figure"]:
            report += f"Filename: [{issue_dict['model_setup_figure']['filename']}]({issue_dict['model_setup_figure']['url']})  \n"
        if "caption" in issue_dict["model_setup_figure"]:
            report += f"Caption: {issue_dict['model_setup_figure']['caption']}  \n"
        if "model_setup_description" in issue_dict:
                #report += "**Model setup description:**  \n"
                report += f"Description:  {issue_dict['model_setup_description']}\n\n"
        report += '  \n'

    # description
    #if "model_setup_description" in issue_dict:
    #    report += "**Model setup description:**  \n"
    #    report += f"{issue_dict['model_setup_description']}\n\n"

    if verbose is True:
        report += "  \n ** Dumping dictionary during testing **  \n"
        report += str(issue_dict)

    return report


def dict_to_metadata(issue_dict, mapping_list=default_issue_entity_mapping_list, filter_entities=True, flat_compact_crate=True, timestamp = False):

    """
    Converts an issue dictionary into a standardized metadata format using Research Object Crate (RO-Crate) structure,
    applying entity simplification and mappings based on predefined templates and rules.

    The function performs several key operations:
    - Filters and simplifies entities within the issue dictionary based on a specified template if `filter_entities` is True.
    - Loads a base RO-Crate template and applies direct mappings from the issue dictionary to the RO-Crate structure using `mapping_list`.
    - Allows for custom modifications to the RO-Crate based on specific data within the issue dictionary.
    - Optionally flattens the RO-Crate structure for a more compact representation if `flat_compact_crate` is True.

    Parameters:
    - issue_dict (dict): The issue dictionary containing data that needs to be converted into metadata.
    - mapping_list (list): A list of mappings that define how elements in the issue dictionary correspond to elements in the RO-Crate structure.
    - filter_entities (bool, optional): If True, simplifies entities in the issue dictionary using predefined templates. Defaults to True.
    - flat_compact_crate (bool, optional): If True, flattens the RO-Crate structure to bring nested entities to the top level. Defaults to True.

    Returns:
    - str: A JSON string representing the metadata in the RO-Crate format.

    Note:
    The function relies on external functions to load entity templates, apply mappings, and customize the RO-Crate. These functions need to be defined separately.
    """




    # Perform a deep copy of the issue_dict to avoid modifying the input dictionary
    issue_dict_copy = copy.deepcopy(issue_dict)

    #this takes the issue_dict and simplifies entities (e.g. @Type=Person) using templates defined at:
    #https://github.com/ModelAtlasofTheEarth/metadata_schema/blob/main/mate_ro_crate/type_templates.json
    if filter_entities is True:
        entity_template = load_entity_template()
        recursively_filter_key(issue_dict_copy, entity_template)

    #load the RO-Crate template as a Python dictionary
    #$print(ro_crate.keys())
    #>>>dict_keys(['@context', '@graph'])
    ro_crate = load_crate_template()

    #Apply direct mappings between the issue_dict and the RO-Crate
    dict_to_ro_crate_mapping(ro_crate, issue_dict_copy,  mapping_list)

    #Add any further direct changes to the RO-Crate based on issue_dict
    defaults_and_customise_ro_crate(issue_dict_copy, ro_crate, timestamp=timestamp)


    #flatten the crate (brings nested entities to the top level)
    if flat_compact_crate is True:
        flatten_crate(ro_crate)
        # flatten a document
        # see: https://json-ld.org/spec/latest/json-ld/#flattened-document-form
        # all deep-level trees flattened to the top-level
        #ro_crate= jsonld.flatten(ro_crate)

    metadata_out = json.dumps(ro_crate)

    return metadata_out

def dict_to_yaml(issue_dict, timestamp = False):
    '''

    Returns:
    - str: a string representing the markdown with YAML frontmatter

    '''
    yaml_dict = {}
    #map the issue dict through to the yaml_dict
    map_dictionaries(yaml_dict, issue_dict, issue_yaml_mapping)
    #this function makes some further changes,
    #basically applies fixed so yaml_dict is configured correctly
    configure_yaml_output_dict(yaml_dict, issue_dict, timestamp =timestamp)

    #convert the dictionary YAML string using ruamel.yaml

    #yaml_string = Ryaml.dump_to_string(yaml_dict)
    #formatted_yaml_string = save_yaml_with_header(yaml_string)

    #the string returned should be in approapriate format
    #to write directly to the ./website/graphics
    return yaml_dict
    #return formatted_yaml_string
