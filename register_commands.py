import requests

# Find these in the Discord Developer Portal
APP_ID = "YOUR_APPLICATION_ID"
BOT_TOKEN = "YOUR_BOT_TOKEN"

url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
headers = {
    "Authorization": f"Bot {BOT_TOKEN}",
    "Content-Type": "application/json"
}

# Define the JSON structure for your commands
commands = [
    {
        "name": "list",
        "description": "View the server to-do list",
        "type": 1
    },
    {
        "name": "add",
        "description": "Add a task to the server list",
        "type": 1,
        "options": [
            {
                "name": "task",
                "description": "The task to add",
                "type": 3, # Type 3 is a String
                "required": True
            }
        ]
    },
    {
        "name": "done",
        "description": "Remove a task by its ID",
        "type": 1,
        "options": [
            {
                "name": "task_id",
                "description": "The ID of the task",
                "type": 4, # Type 4 is an Integer
                "required": True
            }
        ]
    }
]

# Send the commands to Discord
response = requests.put(url, headers=headers, json=commands)

if response.status_code == 200:
    print("✅ Commands registered successfully!")
else:
    print(f"❌ Failed to register commands: {response.status_code}\n{response.json()}")