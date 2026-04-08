from sqlalchemy.orm import Session
from models_task import User, Tasks
from schema import UserCreate, TaskCreate
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from schema import TaskCreate, TaskPublic, UserCreate, UserPublic

from fastapi import Depends
from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import get_db
from models_task import User, Tasks


def create_user(db: Session, user: UserCreate):
    user = User(**user.model_dump())
    print(type(user))
    db.add(user)
    db.commit()
    db.refresh(user)
    print(user)

    return user


def get_user(db: Session, user_id: int):
    user_id = db.get(User, user_id)
    print(user_id)

    return user_id

def get_all_users(db: Session):
    users = db.query(User).all()
    print(users)

    return users

def create_task(db: Session, task: TaskCreate, user_id: int) -> TaskCreate:
    task_data = task.model_dump()
    task = Tasks(**task_data, user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    task_dict = TaskPublic.model_validate(task)
    # task_dict["user_id"] = user_id
    # task_dict = TaskPublic(**task_dict)
    #pydantic moddel for input validation -> sqlmodel for table mapping -> insert to db
    # -> pydantic model for output validation
    return task_dict


def get_tasks_for_user(db: Session, user_id: int):
    tasks = db.query(Tasks).filter(Tasks.user_id == user_id).all()
    print(tasks)

    return tasks



