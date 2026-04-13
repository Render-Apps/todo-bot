import os
from flask import Flask, request, jsonify
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import database

app = Flask(__name__)

PUBLIC_KEY = os.environ.get('DISCORD_PUBLIC_KEY', '').strip()

@app.route('/api/interactions', methods=['POST'])
def interactions():
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    
    raw_body = request.get_data()

    if not signature or not timestamp or not PUBLIC_KEY:
        return 'Missing required headers or configuration', 400

    try:
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(
            timestamp.encode() + raw_body, 
            bytes.fromhex(signature)
        )
    except (BadSignatureError, ValueError):
        return 'Invalid request signature', 401

    data = request.json

    if data['type'] == 1:
        return jsonify({"type": 1})

    if data['type'] == 2:
        command_name = data['data']['name']
        
        THEME_COLOR = 16678937 

        if command_name == 'list':
            tasks = database.get_tasks()
            if not tasks:
                return jsonify({
                    "type": 4, 
                    "data": {
                        "embeds": [{
                            "title": "📋 Server To-Do List",
                            "description": "*The list is currently empty! Use `/add` to create a task.*",
                            "color": THEME_COLOR
                        }]
                    }
                })
            
            # Format the tasks nicely
            description_text = ""
            for task_id, task in tasks:
                description_text += f"**`{task_id}`** {task}\n"
                
            return jsonify({
                "type": 4, 
                "data": {
                    "embeds": [{
                        "title": "📋 Server To-Do List",
                        "description": description_text,
                        "color": THEME_COLOR
                    }]
                }
            })

        elif command_name == 'add':
            task_content = data['data']['options'][0]['value']
            database.add_task(task_content)
            return jsonify({
                "type": 4, 
                "data": {
                    "embeds": [{
                        "description": f"✅ **Added:** {task_content}",
                        "color": 5763719 # Green success color
                    }]
                }
            })

        elif command_name == 'done':
            task_id = data['data']['options'][0]['value']
            success = database.remove_task(task_id)
            if success:
                return jsonify({
                    "type": 4, 
                    "data": {
                        "embeds": [{
                            "description": f"🗑️ **Removed task:** `{task_id}`",
                            "color": 15548997 # Red deletion color
                        }]
                    }
                })
            else:
                return jsonify({
                    "type": 4, 
                    "data": {
                        "embeds": [{
                            "title": "⚠️ Error",
                            "description": f"Task `{task_id}` not found.",
                            "color": 16776960 # Yellow error color
                        }]
                    }
                })

    return jsonify({"error": "Unknown command"}), 400