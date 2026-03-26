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

def create_task(db: Session, task: TaskCreate, user_id: int):
    task_data = task.model_dump()
    task = Tasks(**task_data, user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    print(task)

    return task


def get_tasks_for_user(db: Session, user_id: int):
    each_task = db.query(Tasks).filter(Tasks.user_id == user_id).all()
    print(each_task)

    return each_task



