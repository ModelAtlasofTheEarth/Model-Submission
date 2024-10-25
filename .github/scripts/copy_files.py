import requests
from github.GithubException import UnknownObjectException

#def copy_files(repo, directory, issue_dict):
#	file_keys = ["landing_image", "animation", "graphic_abstract", "model_setup_figure"]

#	for file_key in file_keys:
#		if file_key in issue_dict:
#			response = requests.get(issue_dict[file_key]["url"])
#			repo.create_file(directory+issue_dict[file_key]["filename"], "add "+issue_dict[file_key]["filename"], response.content)


def copy_files(repo, directory, issue_dict):
    file_keys = ["landing_image", "animation", "graphic_abstract", "model_setup_figure"]

    for file_key in file_keys:
        if file_key in issue_dict:
            file_info = issue_dict[file_key]
            url = file_info.get("url", "")

            # Skip if the URL is an empty string
            if url:
                file_path = directory + file_info["filename"]

                # Skip if file already exists in repo
                file_exists = False
                try:
                    file_content = repo.get_contents(file_path)
                    file_exists = True
                except UnknownObjectException:
                    file_exists = False

                if file_exists:
                    print(f"Skipping {file_key} as the file already exists")
                else:
                    response = requests.get(url)
                    repo.create_file(file_path, "add " + file_info["filename"], response.content)
            else:
                print(f"Skipping {file_key} as the URL is empty")
