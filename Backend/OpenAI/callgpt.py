import openai
import os
from pymongo import MongoClient
openai.api_key = ""
client = MongoClient('mongodb://localhost:27017/')
db = client.GitChat
collection = db.ChatStorage
'''
import together

together.api_key = ""

togetherclient = openai.OpenAI(
    api_key="",
    base_url="https://api.together.xyz/v1",
)

def getanswer(messages: list, session_id: str) -> str:
    if len(messages) >= 5:
        messages = list(messages[0]) + messages[-3:]
    chat_completion = togetherclient.chat.completions.create(
        model="teknium/OpenHermes-2p5-Mistral-7B",
        messages=messages,
        temperature=0.7,
        max_tokens=3072)
    response = chat_completion.choices[0].message.content
    collection.update_one({"session_id": session_id}, {"$push": {"frontend": {"role": "assistant", "content": response}}})
    
      
    return response



'''



#MESSEGES OVER HERE NEEDS TO BE FRONTEND MESSAGES
def getfilenamestopull(filemessages, filelist) -> str:
    response = openai.chat.completions.create(
    model="gpt-4-1106-preview",
    response_format={ "type": "json_object" },
    messages=filemessages
    )
    return response.choices[0].message.content 







def getanswer(messages: list, session_id: str) -> str:
    try:
        messages = [messages[0], messages[-1]]

        response = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        stream=True
        )
        document = collection.find_one({"session_id": session_id})
    
        prompts_length = len(document['frontend'])
        last_element_index = prompts_length 
        last_element_content = f"frontend.{last_element_index}.content"
        last_element_role = f"frontend.{last_element_index}.role"

        reply_content = ""
        if response is not None:
            for chunk in response:
                if chunk.choices[0].delta.content: 
                    reply_content += chunk.choices[0].delta.content
                    # Update the MongoDB document
                    collection.update_one(
                        {"session_id": session_id},
                        {"$set": {last_element_content: reply_content, last_element_role: "assistant"}}
                    )  
    except:
        reply_content = "Sorry, there was an error. Please try again. :3"
        collection.update_one({"session_id": session_id},{"$pop": {"prompts": 1}})
        collection.update_one({"session_id": session_id}, {"$push": {"frontend": {"role": "assistant", "content": reply_content}}})
    return reply_content

