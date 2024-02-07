import os
from github import Github, Auth
from parse_issue import parse_issue
from crosswalks import dict_to_report

# Environment variables
token = os.environ.get("GITHUB_TOKEN")
issue_number = int(os.environ.get("ISSUE_NUMBER"))

# Get issue
auth = Auth.Token(token)
g = Github(auth=auth)
repo = g.get_repo("ModelAtlasofTheEarth/Model_Submission")
issue = repo.get_issue(number = issue_number)

# Parse issue
data, error_log = parse_issue(issue)

# Write report
report = "Thank you for submitting. Please check the output below, and fix any errors, etc.\n\n"

report = """Thank you for submitting. \n 
* Using Github actions, we have regenerated a report summarising information about your model \n 
* Please check the report below, particularly the warning and errors section, and website materials \n 
* You can fix any errors, or update fields, by editing the markdown file at the top of the issue \n 
* Edits will trigger the report will be regenerated \n 
* once you are satisfied with the results, please add an https://github.com/ModelAtlasofTheEarth/Model_Submission/labels/review%20requested \n 
* once the `model_reviewers` team has approved the model, we will create a repository for your model \n\n""" 

report += "# Errors and Warnings \n"
report += error_log + "\n\n"

report += "# Parsed data \n"
report += dict_to_report(data)

# Post report to issue as a comment
issue.create_comment(report)
