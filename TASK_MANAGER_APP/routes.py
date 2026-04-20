from schema import TaskCreate  
from schema import TaskPublic
from schema import UserCreate
from schema import UserPublic
from sqlalchemy.orm import Session
from database import get_db
from models import User, Tasks



def create_user(db: Session, user: UserCreate):
    user = User(**user.model_dump())
    print(type(user))
    db.add(user)
    db.commit()
    db.refresh(user)
    print(user)

    return user

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



def get_all_users(db: Session, offset: int = 0, limit: int = 10) -> UserPublic:
    users = db.query(User).offset(offset).limit(limit).all()

    return users



def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()

    return user


def get_tasks_for_user(db: Session, user_id: int):
    tasks = db.query(Tasks).filter(Tasks.user_id == user_id).all()
    print(tasks)

    return tasks

def delete_user(db: Session, user_id: int):
    user = db.get(User, user_id)
    db.delete(user)
    db.commit()

    return user