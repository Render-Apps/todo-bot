import os
from flask import Flask, request, jsonify
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import database

app = Flask(__name__)

# This is found in the Discord Developer Portal -> General Information
PUBLIC_KEY = os.environ.get('DISCORD_PUBLIC_KEY')

@app.route('/api/interactions', methods=['POST'])
def interactions():
    # 1. Verify the Request comes from Discord
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.get_data().decode('utf-8')

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        return 'Invalid request signature', 401

    # 2. Parse the Command
    data = request.json

    # Discord's initial ping to verify your endpoint is alive
    if data['type'] == 1:
        return jsonify({"type": 1})

    # Slash Command Execution
    if data['type'] == 2:
        command_name = data['data']['name']

        if command_name == 'list':
            tasks = database.get_tasks()
            if not tasks:
                return jsonify({"type": 4, "data": {"content": "The server to-do list is empty!"}})
            
            response_text = "**Server To-Do List:**\n"
            for task_id, task in tasks:
                response_text += f"`{task_id}`: {task}\n"
            return jsonify({"type": 4, "data": {"content": response_text}})

        elif command_name == 'add':
            # Extract the user's string input from the JSON payload
            task_content = data['data']['options'][0]['value']
            database.add_task(task_content)
            return jsonify({"type": 4, "data": {"content": f"✅ Added: {task_content}"}})

        elif command_name == 'done':
            # Extract the integer input from the JSON payload
            task_id = data['data']['options'][0]['value']
            success = database.remove_task(task_id)
            if success:
                return jsonify({"type": 4, "data": {"content": f"🗑️ Removed task `{task_id}`"}})
            else:
                return jsonify({"type": 4, "data": {"content": f"⚠️ Task `{task_id}` not found."}})

    return jsonify({"error": "Unknown command"}), 400