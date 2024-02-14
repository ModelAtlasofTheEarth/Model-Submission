import os
from github import Github, Auth

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")

    org_name = os.environ.get("OWNER")
    repo_name = os.environ.get("REPO")
    issue_number = os.environ.get("ISSUE_NUMBER")

    user_login = os.environ.get("USER")

    # Get user and team
    auth = Auth.Token(token)
    g = Github(auth=auth)
    org = g.get_organization(org_name)
	
    user = g.get_user(user_login)
    team = org.get_team_by_slug("model_reviewers")

    # Check if user in team
    authorized = team.has_in_members(user)

    if not authorized:
        # Remove approved label because it isn't
        issue = org.get_repo(repo_name).get_issue(number = issue_number)
        issue.remove_from_labels("approved")

    print(authorized)