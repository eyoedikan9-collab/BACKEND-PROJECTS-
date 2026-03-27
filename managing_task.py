import psycopg2

conn = psycopg2.connect(
    database="task_db",
    user="postgres",
    password="justgetout",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

def add_task():
    task_ = input("Enter task: ").strip().lower()
    date_time = input("Enter task time: ").strip().lower()
    duration = input("Enter task duration: ").strip().lower()
    is_completed = input("Input 'completed' if task is completed: ").strip().lower()
    add_task_query = """
    INSERT INTO tasks(task, created_at, duration, is_completed)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(add_task_query, (task_, date_time, duration, is_completed))
    conn.commit()
    print("Task added successfully!")


def view_task():
    cur.execute(f"SELECT * FROM tasks;")
    rows = cur.fetchall()
    for row in rows:
        print(row)

def mark_task():
    view_task()
    task_name = input("What is the name of the task you want to mark as complete? ").strip().lower()
    cur.execute("UPDATE tasks SET is_completed = 'completed' WHERE task = %s", (task_name,))
    conn.commit()
    print("Status updated successfully!")
def delete_task():
    view_task()
    del_task = input("Enter name of task to be deleted: ").strip().lower()
    cur.execute("DELETE FROM tasks WHERE task = %s", (del_task,))
    conn.commit()
    print("Deleted successfully!")
def task_menu():
    print("""
    1. Add Task
    2. View Task 
    3. Mark Task as complete
    4. Delete Task
    5. Exit Task 
       """)
    user_choice = int(input("What do you want to do ?"))

    if user_choice in range(1, 6):
        if user_choice == 1:
            add_task()
        elif user_choice == 2:
            view_task() 
        elif user_choice == 3:
            mark_task() 
        elif user_choice == 4:
            delete_task()
        elif user_choice == 5:
            return "Exit"         
    else:
        print("Invalid choice please check and try again")
while True:
    output = task_menu()
    if output == "Exit":
        break
cur.close()
conn.close()