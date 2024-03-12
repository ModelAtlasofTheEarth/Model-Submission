import os
from github import Github, Auth
from parse_issue import parse_issue
from crosswalks import dict_to_metadata, dict_to_yaml, dict_to_report
from yaml_utils import format_yaml_string
from copy_files import copy_files
from ruamel.yaml import YAML
import io
import json

# Environment variables
token = os.environ.get("GITHUB_TOKEN")
issue_number = int(os.environ.get("ISSUE_NUMBER"))
model_owner = os.environ.get("OWNER")
model_repo_name = os.environ.get("REPO")


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
metadata = dict_to_metadata(data, flat_compact_crate=False)

#FOR TESTING - print out dictionary as a comment
issue.create_comment("# M@TE crate \n"+str(metadata))

# Move files to repo
model_repo.create_file("ro-crate-metadata.json","add ro-crate",metadata)
#we should do this this as part of the copy to website action
model_repo.create_file("website_material/ro-crate-metadata.json","add ro-crate",metadata)

#######
#Save the trail of metadata sources to .metadata_trail
issue_dict_str = json.dumps(data)
model_repo.create_file(".metadata_trail/issue_body.md","add issue_body", issue.body)
model_repo.create_file(".metadata_trail/issue_dict.json","add issue_dict", issue_dict_str)

#####Create the README.md

pre_report = '# New [M@TE](https://mate.science/)!: \n ' +  '_we have provided a summary of your model as a starting point for the README, feel free to edit_' + '\n'
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
# fomat and write the web YAML
web_yaml_dict = dict_to_yaml(data)
yaml_content_with_frontmatter = format_yaml_string(web_yaml_dict)
commit_message = 'Add YAML file with front matter'
model_repo.create_file("website_material/index.md", commit_message, yaml_content_with_frontmatter)


# Copy web material to repo
copy_files(model_repo, "website_material/graphics/", data)



# Report creation of repository
issue.create_comment(f"Model repository created at https://github.com/{model_owner}/{model_repo_name}")
