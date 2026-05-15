from pwdlib import PasswordHash
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from schema import UserPublic
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS 
from typing import Annotated 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


password_hash = PasswordHash.recommended()



def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        print(type(ACCESS_TOKEN_EXPIRE_MINUTES))
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)    
   
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)    
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 
        user_id = payload.get("sub")
        if user_id is None:            
            raise credentials_exception  
          
    except JWTError:        
        raise credentials_exception 
       
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    user = db.query(User).filter(User.user_id == int(user_id)).first()    
    if user is None:        
            raise credentials_exception
    user = UserPublic.model_validate(user) 
  
    return user

 
def get_current_admin_user(current_user: Annotated[(User, Depends(get_current_user))]):
    if current_user.role != "admin":
                raise HTTPException(status_code=401, detail="User not admin")
    return current_user



# h = hash_password("hello")
# print(h)                                
# print(verify_password("hello", h)) 
# print(verify_password("wrong", h)) 