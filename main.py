from fastapi import FastAPI
from fastapi import status, HTTPException
import uvicorn
import uuid
from pydantic import BaseModel
from typing import List


class TaskCreate(BaseModel):
    task: str
    time: str

class TaskPublic(BaseModel):
    id: str
    task: str
    time: str

app = FastAPI(title="Todo app")

tasks = [
    {"id": "12345", "task": "Go to the gym", "time": "2024-06-01T10:00:00"},
    {"id": "12346", "task": "Go to the market", "time": "2024-06-01T10:00:00"},
    {"id": "12347", "task": "Read a book", "time": "2024-06-02T08:00:00"},
    {"id": "12348", "task": "Cook dinner", "time": "2024-06-02T18:00:00"},
    {"id": "12349", "task": "Call mom", "time": "2024-06-02T12:00:00"},
    {"id": "12350", "task": "Pay electricity bill", "time": "2024-06-03T09:00:00"},
    {"id": "12392", "task": "Subscribe to newsletter", "time": "2024-06-17T09:00:00"},
    {"id": "12393", "task": "Donate old clothes", "time": "2024-06-17T13:00:00"},
    {"id": "12394", "task": "Set up savings account", "time": "2024-06-17T15:00:00"},
    {"id": "12395", "task": "Paint bedroom wall", "time": "2024-06-18T10:00:00"},
    {"id": "12396", "task": "Practice guitar", "time": "2024-06-18T18:00:00"},
]

@app.get("/tasks", response_model=List[TaskPublic])
def get_tasks():
    print("This resource was accessed")
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskPublic)
def get_task_by_id(task_id: str):
    print("This resource was accessed")
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No task found with id {task_id}")

@app.post("/task", status_code=status.HTTP_201_CREATED)
def create_task(param: TaskCreate):
    id_ = f"{uuid.uuid4()}"[:5]
    tasks.append({"task": param.task, "time": param.time, "id":id_})

    # return {"message": "Task created successfully"}

@app.delete("/task/{task_id}", response_model=dict)
def delete_task(task_id: str):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return {"status":f"Item with id {task_id} successfully deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No task found with id {task_id}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)


#input and output validation with pydantic, defining a respoonse model
#pagination with offset and limit
#exception handling with HTTPException
