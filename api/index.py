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

    # API verification
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

        # Commands
        if command_name == 'list':
            tasks = database.get_tasks()
            
            # Empty Return
            if not tasks:
                return jsonify({"type": 4, "data": {"embeds": [{"title": "📋 Server To-Do List", "description": "*The list is empty! Use `/add` or `/multi_add`.*", "color": THEME_COLOR}]}})
            
            # "Type" Checking
            list_type = data['data']['options'][0]['value']

            # Get pending and done tasks
            pending = [t for t in tasks if not t[2]] # not done
            done = [t for t in tasks if t[2]] # done

            if not list_type:
                list_type = 0

            if list_type == 0 or list_type == 2:
                pending_text = ""
                for i, (task_id, task, _) in enumerate(pending, 1):
                    pending_text += f"**{i}.** (id: `{task_id}`) {task}\n"
                
                if not pending_text:
                    pending_text = "*All caught up!*"

                embeds = [{
                    "title": "📋 Server To-Do List",
                    "description": "**📝 Pending Tasks**\n" + pending_text,
                    "color": THEME_COLOR
                }]

            if done and (list_type == 0 or list_type == 2):
                done_text = ""
                for i, (task_id, task, _) in enumerate(done, 1):
                    done_text += f"~~**{i}.** (id: `{task_id}`) {task}~~\n"
                
                embeds.append({
                    "title": "✅ Completed Tasks",
                    "description": done_text,
                    "color": 5763719
                })
                
            return jsonify({"type": 4, "data": {"embeds": embeds}})

        elif command_name == 'add':
            task_content = data['data']['options'][0]['value']
            database.add_task(task_content)
            return jsonify({"type": 4, "data": {"embeds": [{"description": f"✅ **Added:** {task_content}", "color": 5763719}]}})

        elif command_name == 'multi_add':
            csv_content = data['data']['options'][0]['value']
            tasks_to_insert = [t.strip() for t in csv_content.split(',') if t.strip()]
            
            if tasks_to_insert:
                database.add_multiple_tasks(tasks_to_insert)
                list_str = "\n".join([f"• {t}" for t in tasks_to_insert])
                return jsonify({"type": 4, "data": {"embeds": [{"description": f"✅ **Added {len(tasks_to_insert)} tasks:**\n{list_str}", "color": 5763719}]}})
            else:
                return jsonify({"type": 4, "data": {"embeds": [{"description": "⚠️ No valid tasks found. Format: `Task 1, Task 2`", "color": 16776960}]}})

        elif command_name == 'done':
            task_id = data['data']['options'][0]['value']
            success = database.mark_task_done(task_id)
            if success:
                return jsonify({"type": 4, "data": {"embeds": [{"description": f"✅ **Marked task as done:** `{task_id}`", "color": 5763719}]}})
            else:
                return jsonify({"type": 4, "data": {"embeds": [{"title": "⚠️ Error", "description": f"Task `{task_id}` not found.", "color": 16776960}]}})

    return jsonify({"error": "Unknown command"}), 400