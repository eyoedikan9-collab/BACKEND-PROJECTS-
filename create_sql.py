import psycopg2

create_task_query = """
CREATE TABLE IF NOT EXISTS
tasks(
    id serial PRIMARY KEY,
    task VARCHAR(255) NOT NULL, 
    created_at TIMESTAMP DEFAULT NOW(),
    duration VARCHAR NOT NULL,
    status VARCHAR(255) NOT NULL
    )
"""

conn = psycopg2.connect(
    database="taskmanager",
    user="root",
    password="root",
    host="localhost",
    port="5432"
)
def create_tables():
    cur = conn.cursor()
    cur.execute(create_task_query)
    conn.commit()
    cur.close()
    conn.close()

create_tables()
