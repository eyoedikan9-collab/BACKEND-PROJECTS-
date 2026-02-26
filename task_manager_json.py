import json
def add_task():
    task_ = input("Enter task: ")
    date_time = input("Enter task time: ")
    duration = input("Enter task duration: ")
    new_task_data = {"Task": task_, "Date/Time": date_time, "Duration": duration}
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
            # if isinstance(data, dict):
            #     data = [data]
            # list = []
            # list.append(data)
            # for task in data:
            print(data)

    except FileNotFoundError:
        print("Nothing Found in json")
def mark_task():
    task_name = input("What is the name of the task you want to mark as complete? ")
    print(task_name)
    status_ = input("Status: ")
    print(status_)
    key = "Status"
    set_status = ["Completed", "Pending"]
    if status_ not in set_status:
                print("Invalid status choice, please check and try again")
                task_menu()
    else:
        with open('task.json', 'r') as f:
            data = json.load(f)
            part_task = data['Task'] == task_name
            if part_task:
                data[key] = status_
                
    #     for new_task_data in data:
    #                 getting = new_task_data.get("Task")
    # if task_name in getting:
    #     status_ = input("Status: ")
            
    # set_status = ["Completed", "Pending"]
    # if status_ not in set_status:
    #     print("Invalid status choice, please check and try again")
    # else:
           
    #     print(f"Status :{status_} is being added to {getting} task")
def delete_task():
    del_task = input("Enter name of task to be deleted: ")
    print(del_task)
    with open('task.json', 'r') as f:
        data = json.load(f)
        for task in data:
            if data["Task"] == del_task:
                pass
        

      

             

# def exit_task():
#     print('All task save bye')
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
        task_menu()
while True:
    tk_m = task_menu()
    if tk_m == 5
 