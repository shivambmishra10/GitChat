from GitScripts import extracting
import re
import json


from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.GitChat
collection = db.ChatStorage

systemmessage = "You are an LLM exceptionally good at understanding and helping with tasks related to Massive Codebases. Your job is to take a user's prompt, and a subset of the codebase that is auto-added if it might be relevant to the prompt and point the user to relevant code-pieces and answer the user in a concise, consistent manner. Remember to only answer whats important to the prompt and treat the codes only as a reference."



def returnkaro(url, session_id):  #url to contain c lone link
    #url is of type https://github.com/{user}/{repo}.git
    print(url)
    pattern = r"https://github\.com/(.+)/(.+)(?:\.git)?$"
    #print("URL: ", url)
    match = re.search(pattern, url)
    user, repo = match.groups()
    #print(user,repo)
    return [extracting.process_direc_for_filenames(url, session_id), user, repo]

def getGit(details):   #json file
    #print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n DETAILS: ", details)
    try:
        data = details
        dic = data
    except Exception as e:
        print(f"An exception occurred while processing the file: {str(e)}")
        return 1
    #print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", dic)
    link = dic["link"]
    #print("\n\n", link)
    session_id = dic["session_id"]
    # Create a file with the session id as the name
    cummiesinmytummies = returnkaro(link, session_id) # Get the contents of the repo the fucking file structure 
    #print(cummiesinmytummies)
    user = cummiesinmytummies[1]
    repo = cummiesinmytummies[2]
    if collection.find_one({"session_id": session_id}):
        collection.delete_one({"session_id": session_id})
    collection.insert_one({"session_id": session_id,"user": user, "repo": repo, "gitfileslist": cummiesinmytummies[0], "frontend": [], "prompts": [{"role": "system", "content": systemmessage}], "filemesseges": [{"role": "system", "content": "You are an LLM with the job to identify code files in a codebase that are relevant to a user's prompt. You will be provided with the prompt and the exact file names and positions. Reply with a JSON object where the keys are the exact names of the files to contain, and the value set to 1 , containing the exact names of the files you think are relevant to the prompt. It is highly important that the exact names of the files is maintained. If you think no files are relevant, reply with an empty JSON object. If there is a ReadMe file, always include it in the JSON object"}]})   
    return 0


