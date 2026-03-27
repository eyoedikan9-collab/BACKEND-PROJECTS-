import psycopg2

conn = psycopg2.connect(
    database="task_db",
    user="postgres",
    password="justgetout",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
def create_tables():
    cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (id serial PRIMARY KEY, 
                task VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT NOW(), 
                duration VARCHAR NOT NULL, is_completed VARCHAR(255) DEFAULT 'pending');
                """)
    conn.commit()
create_tables()    
cur.close()
conn.close()    