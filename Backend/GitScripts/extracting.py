import requests
from requests.auth import HTTPBasicAuth
import os 
import re
import base64

# Personal access token for authentication
access_token = ''   #remove this before pushing
auth = HTTPBasicAuth('SajayR', access_token)
headers = {'Accept': 'application/vnd.github.v3+json'}

def get_file_contents(url):
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text
    else:
        print(f"Error fetching {url}: {response.status_code} - {response.text}")
        return None



def process_directory(url, path=""):
    contents = get_file_contents(url)
    if contents is None:
        return {}
    
    file_data = {}
    for content in contents:
        if content['type'] == 'dir':
            # Recursively process directories
            directory_contents = process_directory(content['url'], path=content['path'] + '/')
            file_data.update(directory_contents)
        elif content['type'] == 'file':
            if content['size'] < 1000000:  # size limit, consider handling larger files differently
                file_content = get_file_contents(content['download_url'])
                if file_content is not None:
                    file_data[path + content['name']] = file_content
            else:
                print(f"File too large to fetch directly: {content['path']}")
    return file_data


def get_repo_contents(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    rep_contents= process_directory(url)

    allcontents = ""

    for path, content in rep_contents.items():
        allcontents += f"###File Name: {path}\n###Content: \n{content}\n\n"
    return allcontents

def filenames(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    file_paths = process_direc_for_filenames(url)

    # Format the list of paths as a string
    formatted_paths = "\n".join(file_paths)
    return formatted_paths




def process_direc_for_filenames(link, session_id):
    import subprocess
    import os

    # Clone the repository into a folder named "ClonedUserRepo"
    subprocess.run(['git', 'clone', link, f'ClonedUserRepo/{session_id}'], check=True)

    file_paths = []
    for root, dirs, files in os.walk(f'ClonedUserRepo/{session_id}'):
        for file in files:
            # Construct the file path relative to the session_id directory
            file_path = os.path.relpath(os.path.join(root, file), f'ClonedUserRepo/{session_id}')
            file_paths.append(file_path)

    # Remove the "ClonedUserRepo" directory after processing
    #subprocess.run(['rm', '-rf', 'ClonedUserRepo'], check=True)
    
    return file_paths   #returns a list of all fucking file paths

def get_local_file_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    
def get_file_prompt(session_id, file_paths):
    all_contents = ""
    script_dir = os.path.dirname(__file__)
    # Move up one directory to get to the parent of GitScripts
    parent_dir = os.path.dirname(script_dir)
    # Construct the path to the ClonedUserRepo directory
    cloned_repo_path = os.path.join(parent_dir, 'ClonedUserRepo', session_id)
    
    for file_path in file_paths:
        # Get the contents of the file stored locally
        full_file_path = os.path.join(cloned_repo_path, file_path)
        file_text = get_local_file_contents(full_file_path)

        # Skip if file_text is None or empty
        if not file_text:
            print(f"Could not fetch content for {file_path}")
            continue

        all_contents += f"###File Name: {file_path}\n###Content: \n{file_text}\n\n"

    return all_contents if len(all_contents) <25000 else all_contents[:25000]


