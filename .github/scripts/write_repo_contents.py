import os
import re
from github import Github, Auth
from parse_issue import parse_issue
from crosswalks import dict_to_metadata, dict_to_yaml, dict_to_report
from ro_crate_utils import replace_keys_recursive
from yaml_utils import format_yaml_string
from copy_files import copy_files
from ruamel.yaml import YAML
import io
import json
from datetime import datetime
from pyld import jsonld
import copy



# Environment variables
token = os.environ.get("GITHUB_TOKEN")
issue_number = int(os.environ.get("ISSUE_NUMBER"))
model_owner = os.environ.get("OWNER")
model_repo_name = os.environ.get("REPO")


#get the time at which the function os ca
current_utc_datetime = datetime.utcnow()
timestamp = current_utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.000Z')


# Get issue
auth = Auth.Token(token)
g = Github(auth=auth)
repo = g.get_repo("ModelAtlasofTheEarth/Model_Submission")
issue = repo.get_issue(number = issue_number)

# Get model repo
model_repo = g.get_repo(f"{model_owner}/{model_repo_name}")

# Parse issue
data, error_log = parse_issue(issue)

# Convert dictionary to metadata json
rocratestr_nested = dict_to_metadata(data, flat_compact_crate=False, timestamp= timestamp)
rocratedict = json.loads(rocratestr_nested)
default_context_list = copy.deepcopy(rocratedict['@context'])

try:
    #context_list, context_dict = get_default_contexts(context_urls=["https://w3id.org/ro/crate/1.1/context"],
    #     verbose=True)

    #we're going to delete the  rocratedict context, so we expand in terms of the contexts provided by get_default_contexts
    #del rocratedict['@context']

    #ctx = context_dict["@context"]
    # Expand the document using the specific contexts
    # this will get rid of any items that are not defined in the schema
    #expanded = jsonld.expand(rocratedict, options={"expandContext": ctx})

    #flatten the document using the specific contexts
    #flattened = jsonld.flatten(expanded)

    #I have figured out how to compact against multiple contexts, so thise will only compact
    #against the value of context_list[0], which is "https://w3id.org/ro/crate/1.1/context"
    #flat_compacted =  jsonld.compact(flattened , ctx = ctx,
    #                       options={"compactArrays": True, "graph": False})

    #rocratedict.update({'@context':default_context_list})
    #flat_compacted.update({'@context':default_context_list})
    #compacted contains the full the context. We don't need these,URLs are sufficient.
    #flat_compacted['@context'] = rocratedict['@context']

    expanded = jsonld.expand(rocratedict)
    flattened  = jsonld.flatten(expanded)
    rocratedict['@graph'] = flattened
    #this strips the @ from the @ids,
    flatcompact = jsonld.compact(rocratedict, ctx  = default_context_list)
    #add the @ back to type, id
    flatcompact = replace_keys_recursive(flatcompact)

except:
    #use the flattening routine we wrote
    #this is not necessary fully compacted (although we try to build compact records)
    flatcompact = dict_to_metadata(data, flat_compact_crate=True, timestamp= timestamp)


#FOR TESTING - print out dictionary as a comment
#issue.create_comment("# M@TE crate \n"+str(metadata))

# Move files to repo
rocratestr_flatcompact= json.dumps(flatcompact)
model_repo.create_file("ro-crate-metadata.json","add ro-crate", rocratestr_flatcompact)
#we should do this this as part of the copy to website action
model_repo.create_file("website_material/ro-crate-metadata.json","add ro-crate", rocratestr_nested)

#######
#Save the trail of metadata sources to .metadata_trail
issue_dict_str = json.dumps(data)
model_repo.create_file(".metadata_trail/issue_body.md","add issue_body", issue.body)
model_repo.create_file(".metadata_trail/issue_dict.json","add issue_dict", issue_dict_str)

#####Create the README.md

pre_report = '# New [M@TE](https://mate.science/)! model: \n ' +  '_we have provided a summary of your model as a starting point for the README, feel free to edit_' + '\n'
report = dict_to_report(data)
# Path to the README.md file
file_path = 'README.md'
# Retrieve the file to get its SHA and content
file_contents = model_repo.get_contents(file_path)
# Update the README.md file
update_info = model_repo.update_file(
    path=file_path,  # Path to the file in the repository
    message='Updated the README.md',  # Commit message
    content=pre_report + report,  # New content for the file
    sha=file_contents.sha  # SHA of the file to update
)

#######
# Add issue keywords as repository topics
keywords = data["scientific_keywords"]
if data["software"]["keywords"]:
    keywords += data["software"]["keywords"]

#ensure keywords have valid format
def sanitize_string(s):
    return re.sub(r'[^a-z0-9-]','-', s)

keywords = [sanitize_string(item[:50].lower()) for item in keywords]

print(keywords)

model_repo.replace_topics(keywords)


#######
# fomat and write the web YAML
web_yaml_dict = dict_to_yaml(data, timestamp= timestamp)
yaml_content_with_frontmatter = format_yaml_string(web_yaml_dict)
commit_message = 'Add YAML file with front matter'
model_repo.create_file("website_material/index.md", commit_message, yaml_content_with_frontmatter)


# Copy web material to repo
copy_files(model_repo, "website_material/graphics/", data)



# Report creation of repository
issue.create_comment(f"Model repository created at https://github.com/{model_owner}/{model_repo_name}")
