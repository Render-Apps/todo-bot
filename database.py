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
            task TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def add_task(task):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO server_todos (task) VALUES (%s)', (task,))
    conn.commit()
    c.close()
    conn.close()

def get_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, task FROM server_todos ORDER BY id ASC')
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def remove_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM server_todos WHERE id = %s', (task_id,))
    rows_deleted = c.rowcount
    conn.commit()
    c.close()
    conn.close()
    return rows_deleted > 0