from fastapi import FastAPI
import uvicorn
import uuid


app = FastAPI(title="Todo app")

tasks = {}

@app.get("/tasks")
def get_tasks():
    print("This resource was accessed")
    return tasks

@app.post("/task", status_code=201)
def create_task(task: str, time: str):
    id_ = f"{uuid.uuid4()}"[:5]
    tasks[id_] = {"task": task, "time": time}
    # return {"message": "Task created successfully"}

@app.delete("/task/{task_id}")
def delete_task(task_id: str):
    del tasks[task_id]
    # global tasks


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)