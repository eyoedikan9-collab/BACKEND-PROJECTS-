from fastapi import FastAPI
from fastapi import status, HTTPException
import uvicorn
import uuid
from pydantic import BaseModel
from typing import List
from schema import TaskCreate, TaskPublic
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
from crud_task import *

app = FastAPI(title="Todo app")


@app.get("/tasks", response_model=List[TaskPublic])
def get_tasks(db: Session = Depends(get_db)):
    tasks = get_tasks_for_user(db=db, user_id=1)
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskPublic)
def get_task_by_id(task_id: str):
    print("This resource was accessed")
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No task found with id {task_id}")

@app.post("/task", status_code=status.HTTP_201_CREATED, response_model=TaskPublic)
def create_new_task(param: TaskCreate, user_id: int, db: Session = Depends(get_db)):
    created_task = create_task(db, task=param, user_id=user_id)
    return created_task


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
