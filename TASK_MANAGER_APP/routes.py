from schema import TaskCreate  
from schema import TaskPublic
from schema import UserCreate
from schema import UserPublic
from sqlalchemy import select
from database import get_db
from models import User, Tasks
from auth import hash_password
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    plain_password = user.password
    hashed_password = hash_password(plain_password)
    user_data = user.model_dump(exclude={"password"})
    user_stored = User(**user_data, hashed_password=hashed_password)
    db.add(user_stored)
    await db.commit()
    await db.refresh(user_stored)

    return user_stored

async def create_task(db: AsyncSession, task: TaskCreate, user_id: int) -> TaskCreate:
    task_data = task.model_dump()
    task = Tasks(**task_data, user_id=user_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    task_dict = TaskPublic.model_validate(task)
    # task_dict["user_id"] = user_id
    # task_dict = TaskPublic(**task_dict)
    #pydantic moddel for input validation -> sqlmodel for table mapping -> insert to db
    # -> pydantic model for output validation
    return task_dict



async def get_all_users(db: AsyncSession, offset: int = 0, limit: int = 10) -> list[User]:

    result = await db.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all()



async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_tasks_for_user(db: AsyncSession, user_id: int) -> list[Tasks]:
    result = await db.execute(select(Tasks).where(Tasks.user_id == user_id))
    return result.scalars().all()

async def delete_user(db: AsyncSession, user_id: int) -> User | None:
    user = await db.get(User, user_id)
    if user:
        await db.delete(user)
        await db.commit()

    return user


async def update_role(db: AsyncSession, user_id: int, role: str) -> User:
    user = await db.get(User, user_id)
    user.role = role
    await db.commit()
    await db.refresh(user)

    return user

