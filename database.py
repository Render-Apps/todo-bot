import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def setup_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS server_todos (
            id SERIAL PRIMARY KEY,
            guild_id VARCHAR(255),
            task TEXT,
            is_done BOOLEAN DEFAULT FALSE
        )
    ''')
    
    try:
        cursor.execute('ALTER TABLE server_todos ADD COLUMN IF NOT EXISTS guild_id VARCHAR(255);')
    except Exception:
        pass
        
    conn.commit()
    cursor.close()
    conn.close()

def add_task(task, guild_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO server_todos (guild_id, task) VALUES (%s, %s)', (guild_id, task))
    conn.commit()
    c.close()
    conn.close()

def add_multi(task_list, guild_id):
    conn = get_connection()
    c = conn.cursor()
    args = [(guild_id, t) for t in task_list]
    c.executemany('INSERT INTO server_todos (guild_id, task) VALUES (%s, %s)', args)
    conn.commit()
    c.close()
    conn.close()

def get_tasks(guild_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, task, is_done FROM server_todos WHERE guild_id = %s ORDER BY id ASC', (guild_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def mark_task_done(task_id, guild_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE server_todos SET is_done = TRUE WHERE id = %s AND guild_id = %s', (task_id, guild_id))
    rows_updated = c.rowcount
    conn.commit()
    c.close()
    conn.close()
    return rows_updated > 0

def mark_multi_done(task_list, guild_id):
    conn = get_connection()
    c = conn.cursor()
    args = [(t, guild_id) for t in task_list]
    c.executemany('UPDATE server_todos SET is_done = TRUE WHERE id = %s AND guild_id = %s', args)
    conn.commit()
    c.close()
    conn.close()