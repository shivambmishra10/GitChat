from flask import Flask, jsonify
from pymongo import MongoClient
from OpenAI import callgpt
import json
from GitScripts import extracting
client = MongoClient('mongodb://localhost:27017/')
db = client.GitChat
collection = db.ChatStorage


def getrelevantcode(filemessages, filelist: list, owner, repo, session_id) -> str:
    relevantfiles = callgpt.getfilenamestopull(filemessages, filelist)
    collection.update_one({"session_id": session_id}, {"$push": {"filemesseges": {"role": "assistant", "content": relevantfiles}}})
    relevantfiles = json.loads(relevantfiles)
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", relevantfiles)
    filelists =[i for i in relevantfiles.keys()]
    return extracting.get_file_prompt(session_id, filelists)




def newprompt(prompt: str, session_id: str) -> None:
    #code = collection.find_one({"session_id": session_id})["codebase"]
    filelist = collection.find_one({"session_id": session_id})["gitfileslist"]
    collection.update_one({"session_id": session_id}, {"$push": {"frontend": {"role": "user", "content": prompt}}})
    filesforprompt = "\n".join(filelist)
    collection.update_one({"session_id": session_id}, {"$push": {"filemesseges": {"role": "user", "content": f"###Prompt:\n {prompt} ###Code Files:\n{filesforprompt}"}}})
    filemesseges = collection.find_one({"session_id": session_id})["filemesseges"]
    
    owner= collection.find_one({"session_id": session_id})["user"]
    repo= collection.find_one({"session_id": session_id})["repo"]


    code = getrelevantcode(filemesseges, filelist, owner, repo, session_id)

    code = code[:25000] if len(code) > 40000 else code
    collection.update_one({"session_id": session_id}, {"$push": {"prompts": {"role": "user", "content": prompt + "\n" + code}}})
    
    

    messages = collection.find_one({"session_id": session_id})["prompts"]

    answer = callgpt.getanswer(messages, session_id) 
    if answer!="Sorry, there was an error. Please try again.":
        collection.update_one({"session_id": session_id}, {"$push": {"prompts": {"role": "assistant", "content": answer}}})

    return None

       


      
    



    