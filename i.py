from openai import OpenAI
from dotenv import load_dotenv
import simplejson as json
import jsonpickle
from datetime import datetime
import os
from pymongo import MongoClient, errors
from bson import ObjectId
import pymongo
import requests
import certifi
from bs4 import BeautifulSoup
from system import generate_system_message

load_dotenv()
AIclient = OpenAI()

ca = certifi.where()

interview_file_path = os.path.join(os.getcwd(), 'jabari_sessions.json')

def load_sessions():
    if os.path.exists(interview_file_path):
        with open(interview_file_path, "r") as file:
            return json.load(file)
    else:
        return {}
    
def save_sessions(sessions):
    with open(interview_file_path, "w") as file:
        json.dump(sessions, file, indent=4)

# functiion to scrape company's info from the website
def get_company_info(url):
    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        # Extract the cleaned text content
        text_content = soup.get_text(separator=' ')
        # Further clean up the text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        text_content = '\n'.join(chunk for chunk in chunks if chunk)
        return text_content
    
# Define a function to search MongoDB
def mongodb_document_search(jobTitle):
    client = pymongo.MongoClient(os.environ['Loubby_String'], tlsCAFile=ca)
    db = client.loubbyDb
    collection = db.listings

    def ensure_text_index():
        try:
            collection.create_index([("$**", "text")])
            print("Text index created successfully.")
        except errors.ServerSelectionTimeoutError as e:
            print(f"Server selection timeout: {e}")
        except errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
        except Exception as e:
            print(f"Error creating text index: {e}")
    # Call the function to create the text index
    ensure_text_index()

    def convert_data(data):
        if isinstance(data, list):
            return [convert_data(item) for item in data]
        elif isinstance(data, dict):
            return {key: convert_data(value) for key, value in data.items()}
        elif isinstance(data, ObjectId):
            return str(data)
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
    try:
        # First, try an exact match on the 'jobTitle' field
        result = list(collection.find(
            {"jobTitle": jobTitle}).limit(10))
        if result:
            return f"Document retrieved: {convert_data(result)}"
        # If no exact match, try a text search
        results = list(collection.find(
            {"$text": {"$search": jobTitle}}).limit(10))
        if results:
            return f"Documents retrieved: {convert_data(results)}"
        # If still no results, try a regex search
        regex_query = {"jobTitle": {"$regex": jobTitle, "$options": "i"}}
        results = list(collection.find(regex_query).limit(10))
        if results:
            return f"Documents retrieved: {convert_data(results)}"
        return {"error": "No matching documents found"}
    except Exception as e:
        return {"error": str(e)}
    
def jabari(user_id, prompt):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_company_info",
                "description": "Get the company's information from their website or url to help write a comprehensive job description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "the company's url",
                        }
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mongodb_document_search",
                "description": "Fetch a document from MongoDB based on job title",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jobTitle": {
                            "type": "string",
                            "description": "The user query",
                        }
                    },
                    "required": ["jobTitle"],
                },
            },
        }
    ]
    sessions = load_sessions()
    sys_message = generate_system_message(prompt)
    if user_id in sessions:
        MESSAGES = jsonpickle.decode(sessions[user_id])
    else:
        MESSAGES = [
            {"role": "system", "content": sys_message}
        ]
    MESSAGES.append({"role": "user", "content": prompt})
    response = AIclient.chat.completions.create(
        model="gpt-4o",
        messages=MESSAGES,
        response_format={"type": "json_object"},
        tools=tools,
        tool_choice="auto",
        temperature=.2
    )
    
    main_assistant_message = response.choices[0].message.content
    assistant_message = response.choices[0].message
    tool_calls = assistant_message.tool_calls
    if tool_calls:
        available_functions = {
            "get_company_info": get_company_info,
            "mongodb_document_search": mongodb_document_search,
        }
        MESSAGES.append(assistant_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            try:
                function_response = function_to_call(**function_args)
            except Exception as e:
                function_response = {"error": str(e)}
            MESSAGES.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        second_response = AIclient.chat.completions.create(
            model="gpt-4o",
            messages=MESSAGES,
            response_format={"type": "json_object"},
            temperature=.3
        )

        second_response_content = second_response.choices[0].message.content
        MESSAGES.append(
            {'role': 'assistant', 'content': second_response_content})
        sessions[user_id] = jsonpickle.encode(MESSAGES, unpicklable=True)
        save_sessions(sessions)
        return second_response_content
    MESSAGES.append({'role': 'assistant', 'content': main_assistant_message})
    sessions[user_id] = jsonpickle.encode(MESSAGES, unpicklable=True)
    save_sessions(sessions)
    return main_assistant_message

PROMPT = "yes"
result = jabari("JSON_Derulo23", PROMPT)
print(result)

