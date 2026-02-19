import json

# Start menu loop
def task_menu():
    print("1. Add a new task")
    print("2. View current tasks")
    print("3. Mark task as complete")
    print("4. Delete a tasks")
    print("5. Exit program")
    selected_item = int(input())
    return selected_item
task_menu()
    
def validation_for_selections(selections):
    if selections not in range(1, 6):
        raise ValueError('Please select a valid option')
    elif selections == 1:
        add_new_task()
    elif selections == 2:
        view_task()
    elif selections == 3:
        mark_task()
    elif selections == 4:
        delete_task()
    elif selections == 5:
        exit_task()

def add_new_task():
    try:
        new_task_name = input('Name for new task: ')
        description = input('Add optional description: ')
        time = input('Add estimated task time: ')
        duration = input('Duration for new task: ')
        new_task_data = {'Task':new_task_name, 'Description':description, 'Time':time, 'Duration': duration}
        
        with open('list_.json', 'r') as f:
            data = json.load(f)
        data.append(new_task_data)
        print("Task successfully saved")

    except FileNotFoundError:
        print(f'Error occured while trying to create a new task')
        data = []
        data.append(new_task_data)
    finally:
        with open('list_.json', 'w') as f:
            json.dump(data, f)
add_new_task()           
#read the json file
# loop through the list to access each dictionary one at a time
# access the task from each dictionary using the task key
#print each task
def view_task(list_):
    try:

        with open('list_.json', 'r') as f:
            data = json.load(f)
            # print(data)   
            for new_task_data in data:
                getting = new_task_data.get("Task")
                print(f"Previous task: {getting}")
                
                for key, value in new_task_data.items():
                    print(f"{key}: {value}")
                print("\n")
    except FileNotFoundError:
        print("File not found.")
def main():
    list_ = 'list_.json' 
    view_task(list_)   

if __name__ == "__main__":
    main()   
        
#Read the json file,# loop through the list
#  to access each dictionary one at a time
# access the task from each dictionary using the task key to 
#print mark each task as complete then print each task

def mark_task(list_):

    with open('list_.json', 'r') as f:
        data = json.load(f)
        for new_task_data in data:
            getting = new_task_data["Task"]
            print(f"Marking task as complete: {getting}")
            new_task_data['Status'] = 'complete'
            print(f"{new_task_data}, Task is being marked as complete.")

def main():
    list_ = 'list_.json'
    mark_task(list_)

if __name__ == "__main__":
    main()

#Read the json file,# loop through the list
#  to access each dictionary one at a time
# access the task from each dictionary using the task key to 
#delete each task then print that task has successfully been deleted.
def delete_task(list_):
    # try:
    with open('list_.json', 'r') as f:
        data = json.load(f)
        for new_task_data in data:
            getting = new_task_data.get("Task")
            print(f"Task to be deleted: {getting}")
            for key in data.pop():

                print(f"{key} : has been deleted.")
                print("\n")
    # except .....  :
    #      print("There is no task to delete.")
def main():
    list_ = "list_.json"
    delete_task(list_)
if __name__ == "__main__":
    main()


def exit_task():
    print('All task save bye')

