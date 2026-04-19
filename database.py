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
            task TEXT,
            is_done BOOLEAN DEFAULT FALSE
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

def add_multi(task_list):
    conn = get_connection()
    c = conn.cursor()
    # Prepare list of tuples for executemany
    args = [(t,) for t in task_list]
    c.executemany('INSERT INTO server_todos (task) VALUES (%s)', args)
    conn.commit()
    c.close()
    conn.close()

def get_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, task, is_done FROM server_todos ORDER BY id ASC')
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def mark_task_done(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE server_todos SET is_done = TRUE WHERE id = %s', (task_id,))
    rows_updated = c.rowcount
    conn.commit()
    c.close()
    conn.close()
    return rows_updated > 0

def mark_multi_done(task_list):
    conn = get_connection()
    c = conn.cursor()
    # Prepare list of tuples for executemany
    args = [(t,) for t in task_list]
    c.executemany('UPDATE server_todos SET is_done = TRUE WHERE id = %s', args)
    conn.commit()
    c.close()
    conn.close()