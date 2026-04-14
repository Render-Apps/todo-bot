import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Find these in the Discord Developer Portal
APP_ID = os.environ.get("APP_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
headers = {
    "Authorization": f"Bot {BOT_TOKEN}",
    "Content-Type": "application/json"
}

commands = [
    {
        "name": "list",
        "description": "View the server to-do list",
        "type": 1,
        "options": [
            {
                "name": "show_done",
                "description": "(0) to display only ongoing / (1) to display only done / (2) to display both",
                "type": 3,
                "required": False
            }
        ]
    },
    {
        "name": "add",
        "description": "Add a task to the server list",
        "type": 1,
        "options": [
            {
                "name": "task",
                "description": "The task to add",
                "type": 3, 
                "required": True
            }
        ]
    },
    {
        "name": "multi_add",
        "description": "Add multiple tasks separated by commas",
        "type": 1,
        "options": [
            {
                "name": "tasks",
                "description": "e.g. Clean the kitchen, Buy groceries, Walk the dog",
                "type": 3, 
                "required": True
            }
        ]
    },
    {
        "name": "done",
        "description": "Mark a task as done by its ID",
        "type": 1,
        "options": [
            {
                "name": "task_id",
                "description": "The ID of the task",
                "type": 4, 
                "required": True
            }
        ]
    }
]

response = requests.put(url, headers=headers, json=commands)

if response.status_code == 200:
    print("✅ Commands registered successfully!")
else:
    print(f"❌ Failed to register commands: {response.status_code}\n{response.json()}")