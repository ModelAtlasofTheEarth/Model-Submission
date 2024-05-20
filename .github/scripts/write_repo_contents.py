import os
import re
from github import Github, Auth
from parse_issue import parse_issue
from crosswalks import dict_to_metadata, dict_to_yaml, dict_to_report, metadata_to_nci
from ro_crate_utils import replace_keys_recursive, assign_ids
from yaml_utils import format_yaml_string
from request_utils import download_license_text
from copy_files import copy_files
from ruamel.yaml import YAML
import io
from io import StringIO
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
repo = g.get_repo("ModelAtlasofTheEarth/model_submission")
issue = repo.get_issue(number = issue_number)

# Get model repo
model_repo = g.get_repo(f"{model_owner}/{model_repo_name}")

# Parse issue
data, error_log = parse_issue(issue)

# Convert dictionary to metadata json
rocratestr_nested = dict_to_metadata(data, flat_compact_crate=False, timestamp= timestamp)
rocratedict = json.loads(rocratestr_nested)
default_context_list = copy.deepcopy(rocratedict['@context'])
#patch missign ids on Person Records
assign_ids(rocratedict['@graph'])

try:

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
#it would be good to remove this duplication and instead copy the main file across
model_repo.create_file("website_material/ro-crate-metadata.json","add ro-crate", rocratestr_flatcompact)
#we should do this this as part of the copy to website action
model_repo.create_file("metadata_trail/ro-crate-metadata-nested.json", "add nested ro-crate to metadata_trail", rocratestr_nested)

#######
#Save the trail of metadata sources to metadata_trail
issue_dict_str = json.dumps(data)
model_repo.create_file("metadata_trail/issue_body.md","add issue_body", issue.body)
model_repo.create_file("metadata_trail/issue_dict.json","add issue_dict", issue_dict_str)

#######
csv_buffer = StringIO()
#get a iso record as pandas df...
nci_iso_record = metadata_to_nci(rocratedict)
nci_iso_record.to_csv(csv_buffer, index=False)
# Reset buffer position to the beginning
csv_buffer.seek(0)
csv_content = csv_buffer.getvalue()
model_repo.create_file("metadata_trail/nci_iso.csv","add nci_iso record csv", csv_content)

#####Save license

try:
    license_url = str(data['license']['url'])
except:
    license_url = ''
license_txt = download_license_text(license_url)
model_repo.create_file("LICENSE","add license text", license_txt)
model_repo.create_file("website_material/license.txt","add license text", license_txt)


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

#####Add to README.md in subdirectories:

pre_notes = "## Notes:\n"
try:
    notes = data['model_code_inputs']['notes']
except KeyError:
    notes = ""

file_path = 'model_code_inputs/README.md'

# Retrieve the existing content of the README.md file
file_contents = model_repo.get_contents(file_path)
existing_content = file_contents.decoded_content.decode()

# Concatenate the existing content with the new notes
updated_content = existing_content + '\n' + pre_notes + notes

# Update the README.md file with the combined content
update_info = model_repo.update_file(
    path=file_path,
    message='Updated the README.md',
    content=updated_content,
    sha=file_contents.sha
)
print("README.md updated successfully!")


##########
pre_notes = "## Notes:\n"
try:
    notes = data['model_output_data']['notes']
except KeyError:
    notes = ""

file_path = 'model_output_data/README.md'

# Retrieve the existing content of the README.md file
file_contents = model_repo.get_contents(file_path)
existing_content = file_contents.decoded_content.decode()

# Concatenate the existing content with the new notes
updated_content = existing_content + '\n' + pre_notes + notes

# Update the README.md file with the combined content
update_info = model_repo.update_file(
    path=file_path,
    message='Updated the README.md',
    content=updated_content,
    sha=file_contents.sha
)
print("README.md updated successfully!")




#######
# Add issue keywords as repository topics
keywords = []
sciencekeywords = data.get("scientific_keywords", [])
softwarekeywords = data["software"].get("keywords", [])
keywords += sciencekeywords + softwarekeywords

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
