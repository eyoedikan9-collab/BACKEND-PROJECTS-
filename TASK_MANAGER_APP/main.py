from fastapi import FastAPI
from fastapi import status, HTTPException
import uvicorn
from typing import List
from schema import TaskCreate, TaskPublic, UserPublic, UserCreate
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
# from crud_task import *
from routes import get_tasks_for_user
from routes import create_task, create_user
from routes import get_user
from routes import get_all_users
from routes import delete_user
from routes import get_user_by_email
from routes import update_role
from models import User
from fastapi.security import OAuth2PasswordRequestForm
from schema import Token
import auth
from auth import create_access_token
from auth import verify_password
from auth import get_current_admin_user
from auth import create_refresh_token
from schema import RefreshTokenRequest
from jose import jwt, JWTError, ExpiredSignatureError
from config import SECRET_KEY, ALGORITHM
from schema import Token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from models import Base
from database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()




app = FastAPI(title="Todo app", lifespan=lifespan)


@app.post("/auth/refresh")
async def refresh(token: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token.token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    new_access_token = create_access_token(data={"sub": sub})
    return {"access_token": new_access_token, "token_type": "bearer"}



@app.post("/auth/token", response_model=Token) 
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> User:
    user_by_email = await get_user_by_email(db=db, email=form_data.username)
    if not user_by_email or not verify_password(form_data.password, user_by_email.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user_by_email.user_id)}) 
    refresh_token = create_refresh_token({"sub": str(user_by_email.user_id)})
    return {"access_token": token, "token_type": "bearer", "refresh_token": refresh_token}



@app.get("/tasks", response_model=List[TaskPublic]) 
async def get_tasks(db: AsyncSession = Depends(get_db), current_user: UserPublic = Depends(auth.get_current_user)):
    tasks = await get_tasks_for_user(db=db, user_id=current_user.user_id)
    return tasks



@app.get("/user/{user_id}", response_model=UserPublic)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_admin_user)):
    a_user = await get_user(db=db, user_id=user_id)
    if not a_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")

    return a_user


@app.get("/users", response_model=List[UserPublic] )
async def get_users(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_admin_user)):
    all_users = await get_all_users(db=db)
    return all_users


@app.post("/task", status_code=status.HTTP_201_CREATED, response_model=TaskPublic)
async def create_new_task(param: TaskCreate, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_current_user)):
    user_id=1
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")
    created_task = await create_task(db, task=param, user_id=user_id)
    return created_task


@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def create_a_user(param: UserCreate, db: AsyncSession = Depends(get_db)):
    created_user = await create_user(db, user=param)
    return created_user



@app.delete("/user/{user_id}")
async def delete_any_user(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_admin_user)):
    del_user = await delete_user(db=db, user_id=user_id)
    print(del_user)
    if not del_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
    return {f"message": "User deleted successfuly"}
   

@app.patch("/user/{user_id}", response_model=UserPublic)
async def update_user_role(user_id: int, role: str, db: AsyncSession = Depends(get_db)):
    updating_user = await update_role(db=db, user_id=user_id, role=role)
    return updating_user

if __name__ == "__main__":
    uvicorn.run("main:app" , host="127.0.0.1", port=8080, reload=True)


#input and output validation with pydantic, defining a respoonse model
#pagination with offset and limit
#exception handling with HTTPException