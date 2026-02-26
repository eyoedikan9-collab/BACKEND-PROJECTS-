import json

def add_task():
    task_ = input("Enter task: ")
    date_time = input("Enter task time: ")
    duration = input("Enter task duration: ")
    new_task_data = {"Task": task_, "Date/Time": date_time, "Duration": duration, "status": "pending"}
    try:
        with open('task.json', 'r') as f:
            data = json.load(f)
        data.append(new_task_data)
        with open('task.json', 'w') as f:
            data = json.dump(data, f, indent=4)
    except FileNotFoundError:
        data = []
        data.append(new_task_data)
        with open('task.json', 'w') as f:
            data = json.dump(data, f, indent=4)
   
def view_task():
    try:
        with open('task.json', 'r') as f:
            data = json.load(f)
    
        for dict_ in data:
            for key, value in dict_.items():
                print(f"{key}: {value}")
            print("=============")

    except FileNotFoundError:
        print("File does not exist.")


def mark_task():
    view_task()
    task_name = input("What is the name of the task you want to mark as complete? ")
    print(task_name)
    with open('task.json', 'r') as f:
        data = json.load(f)

    for task_details in data:
        if task_details['Task'] == task_name:
            task_details['status'] = 'completed'

    with open('task.json', 'w') as f:
        json.dump(data, f, indent=2)
    

def delete_task():
    view_task()
    del_task = input("Enter name of task to be deleted: ")
    print(del_task)
    with open('task.json', 'r') as f:
        data = json.load(f)
        for task in data:
            if task["Task"] == del_task:
                data.remove(task) 
                print(data)
    


def task_menu():
    print("""
    1. Add Task
    2. View Task 
    3. Mark Task as complete
    4. Delete Task
    5. Exit Task 
       """)
    user_choice = int(input("What do you wnat to do ?"))

    if user_choice in range(1, 6):
        if user_choice == 1:
            print("Adding task")
            add_task()
        elif user_choice == 2:
            print("Viewing task")
            view_task() 
        elif user_choice == 3:
            print("Marking task")
            mark_task() 
        elif user_choice == 4:
            print("Deleting task")
            delete_task()
        elif user_choice == 5:
            print("Exiting program")
            return "Exit"   
    else:
        print("Invalid choice please check and try again")
        # task_menu()


while True:
    output = task_menu()
    if output == "Exit":
        break
 