from dotenv import load_dotenv
from dotenv import dotenv_values
config = dotenv_values(".env")
SECRET_KEY = config["SECRET_KEY"]
ALGORITHM = config["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = config["ACCESS_TOKEN_EXPIRE_MINUTES"]
REFRESH_TOKEN_EXPIRE_DAYS = config["REFRESH_TOKEN_EXPIRE_DAYS"] 

SQLALCHEMY_DATABASE_URL = config["SQLALCHEMY_DATABASE_URL"]