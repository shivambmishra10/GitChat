import os
import requests
from flask import Flask, request, jsonify, make_response
from GitScripts import gitmain, extracting
from flask_cors import CORS
import OpenAI.daddy as chatmain


import threading
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
try:
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("MongoDB is connected!")
except Exception as e:
    print("Unable to connect to the server.", e)
db = client.GitChat
collection = db.ChatStorage



app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "chrome-extension://<extension-id>"}})  #PLS EDIT EXTENSION ID IF GOTTEN


def handle_new_prompt(data):
    prompt = data['prompt']
    session_id = data['session_id']
    
    collection.update_one({"session_id": session_id}, {"$set": {"status": "processing"}})
    #toretrieve = chatmain.newprompt(prompt, session_id) #retrive gitsturct from db 
    #toretrieve is dict, holds file names to retrieve

    chatmain.newprompt(prompt, session_id)
    
    collection.update_one({"session_id": session_id}, {"$set": {"status": "completed"}})
    
    return None


@app.route('/get_file_directory/<sessionId>')
def get_file_directory(sessionId: str):
    print(sessionId)
    session_data = collection.find_one({"session_id": sessionId}, {"gitfileslist": 1})
    #print(session_data)

    #print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n", session_data["gitfileslist"])
    #if session_data and "gitfileslist" in session_data:
    if session_data:
        return jsonify({"file_directory": session_data["gitfileslist"]})
    else:
        return jsonify({"error": f"Session_id: {sessionId} not found"}), 404
    #else:
        #return jsonify({"error": f"Session_id: {sessionId} not found"}), 404

@app.route('/gitget', methods=['POST'])
def getgitfiles():
    session_id = request.cookies.get('sessionId')  # Retrieve sessionId from cookie
    data = request.get_json()
    repo_path = os.path.join(os.getcwd(), f'ClonedUserRepo/{session_id}')
    if os.path.exists(repo_path):
        os.system(f'rm -rf {repo_path}')
    data['session_id'] = session_id  # Make sure to include sessionId in the data
    thread = threading.Thread(target=gitmain.getGit, args=(data,))
    thread.start()
    return jsonify({"message": "Git processing started..."}), 200
    
@app.route('/clear_messeges', methods=['POST'])
def clear_messeges():
    try:
        session_id = request.cookies.get('sessionId')
        frontend = collection.find_one({"session_id": session_id}, {"frontend": 1})
        prompts = collection.find_one({"session_id": session_id}, {"prompts": 1})
        files = collection.find_one({"session_id": session_id}, {"gitfileslist": 1})
        collection.update_one({"session_id": session_id}, {"$set": {"frontend": [], "prompts": [prompts[0]], "gitfileslist": [files[0]]}})
        return jsonify({"message": "Messeges cleared"}), 200
    except Exception as e:
        return jsonify({"error": f"Session_id: {session_id} not found"}), 404


@app.route('/newprompt', methods=['POST'])
def chaosbaby():
    session_id = request.cookies.get('sessionId')  # Retrieve sessionId from cookie
    data = request.get_json()

    if 'prompt' in data and session_id:
        data['session_id'] = session_id  # Make sure to include sessionId in the data
        chat_thread = threading.Thread(target=handle_new_prompt, args=(data,))
        chat_thread.start()
        return jsonify({"message": "Processing new prompt..."}), 202
    else:
        return jsonify({"error": "Missing prompt or session_id"}), 400


@app.route('/get_messages/<session_id>')
def get_messages(session_id: int) -> dict:
    frontend_messages = []
    messages = collection.find_one({"session_id": session_id})

    if messages and "frontend" in messages:
        messages = messages["frontend"]
        if len(messages) == 0:
            return jsonify({"error": f"Session_id: {session_id} not found/No Messages"}), 404
        num = 1  
        for message in messages:
            frontend_message = {
                "num": num,
                "from": "bot" if message["role"]=="assistant" else "User",
                "content": message["content"]
            }
            frontend_messages.append(frontend_message)
            num += 1  
    else:
        return jsonify({"error": f"Session_id: {session_id} not found/No Messages"}), 404

    return jsonify(frontend_messages)




@app.route('/check_status/<session_id>')
def check_status(session_id: int):
    session_data = collection.find_one({"session_id": session_id}, {"status": 1})
    if session_data and "status" in session_data:
        return jsonify({"status": session_data["status"]})
    else:
        return jsonify({"status": "unknown", "error": f"Session_id: {session_id} not found"}), 404



if __name__ == '__main__':
    app.run(threaded=True, debug=True)
