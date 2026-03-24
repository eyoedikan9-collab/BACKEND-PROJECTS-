from pydantic import BaseModel

class TaskCreate(BaseModel):
    task: str
    date_time: str
    duration: str
    

class TaskPublic(BaseModel):
    task_id: int
    task: str
    user_id: int
    date_time: str
    duration: str
   
    
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: str 
    age: int
    
class UserPublic(BaseModel):
    user_id: int    
    first_name: str
    last_name: str
    email: str