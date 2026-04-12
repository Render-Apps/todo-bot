import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def setup_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            task TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def add_task(user_id, task):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO todos (user_id, task) VALUES (%s, %s)', (user_id, task))
    conn.commit()
    c.close()
    conn.close()

def get_tasks(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, task FROM todos WHERE user_id = %s', (user_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def remove_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = %s', (task_id,))
    conn.commit()
    c.close()
    conn.close()