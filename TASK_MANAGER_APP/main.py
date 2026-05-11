from fastapi import FastAPI
from fastapi import status, HTTPException
import uvicorn
from typing import List
from schema import TaskCreate, TaskPublic, UserPublic, UserCreate
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
from crud_task import *
from routes import get_tasks_for_user
from routes import create_task, create_user
from routes import get_user
from routes import get_all_users
from routes import delete_user
from routes import get_user_by_email
from models import User
from fastapi.security import OAuth2PasswordRequestForm
from schema import Token
import auth
from auth import create_access_token
from auth import verify_password
 


app = FastAPI(title="Todo app")

@app.post("/auth/token", response_model=Token) 
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> User:
    user_by_email = get_user_by_email(db=db, email=form_data.username)
    if not user_by_email or not verify_password(form_data.password, user_by_email.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user_by_email.user_id)}) 
    return {"access_token": token, "token_type": "bearer"}



@app.get("/tasks/{user_id}", response_model=List[TaskPublic]) 
def get_tasks(user_id: int, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")
    tasks = get_tasks_for_user(db=db, user_id=user_id)
    return tasks


@app.get("/user/{user_id}", response_model=UserPublic)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    a_user = get_user(db=db, user_id=user_id)
    if not a_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")

    return a_user


@app.get("/users", response_model=List[UserPublic])
def get_users(db: Session = Depends(get_db)):
    all_users = get_all_users(db=db)
    return all_users


@app.post("/task", status_code=status.HTTP_201_CREATED, response_model=TaskPublic)
def create_new_task(param: TaskCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    user_id=4
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")
    created_task = create_task(db, task=param, user_id=user_id)
    return created_task


@app.post("/user", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def create_a_user(param: UserCreate, db: Session = Depends(get_db)):
    created_user = create_user(db, user=param)
    return created_user



@app.delete("/user/{user_id}")
def delete_any_user(user_id: int, db: Session = Depends(get_db)):
    del_user = delete_user(db=db, user_id=user_id)
    print(del_user)
    if not del_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
    return {f"message": "User deleted successfuly"}
   


if __name__ == "__main__":
    uvicorn.run("main:app" , host="127.0.0.1", port=8080, reload=True)


#input and output validation with pydantic, defining a respoonse model
#pagination with offset and limit
#exception handling with HTTPException