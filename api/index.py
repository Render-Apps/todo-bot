import os
from flask import Flask, request, jsonify
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import database

app = Flask(__name__)

# Use .strip() to ensure no hidden spaces or newlines break the hex conversion
PUBLIC_KEY = os.environ.get('DISCORD_PUBLIC_KEY', '').strip()

@app.route('/api/interactions', methods=['POST'])
def interactions():
    # 1. Capture Raw Data for Verification
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    
    # CRITICAL: We use get_data() as raw bytes, NO .decode() here
    raw_body = request.get_data()

    if not signature or not timestamp or not PUBLIC_KEY:
        return 'Missing required headers or configuration', 400

    # 2. Cryptographic Verification (Raw Bytes Method)
    try:
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        # Concatenate timestamp bytes and body bytes directly
        verify_key.verify(
            timestamp.encode() + raw_body, 
            bytes.fromhex(signature)
        )
    except (BadSignatureError, ValueError):
        return 'Invalid request signature', 401

    # 3. Parse JSON for Logic (Only AFTER verification)
    data = request.json

    if data['type'] == 1:
        return jsonify({"type": 1})

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
            task_content = data['data']['options'][0]['value']
            database.add_task(task_content)
            return jsonify({"type": 4, "data": {"content": f"✅ Added: {task_content}"}})

        elif command_name == 'done':
            task_id = data['data']['options'][0]['value']
            success = database.remove_task(task_id)
            if success:
                return jsonify({"type": 4, "data": {"content": f"🗑️ Removed task `{task_id}`"}})
            else:
                return jsonify({"type": 4, "data": {"content": f"⚠️ Task `{task_id}` not found."}})

    return jsonify({"error": "Unknown command"}), 400