from sqlalchemy import create_engine
from dotenv import load_dotenv
from dotenv import dotenv_values
from sqlalchemy.orm import sessionmaker

load_dotenv()
config = dotenv_values("TASK_MANAGER_APP/.env")
user = config["POSTGRES_USER"]
password = config["POSTGRES_PASSWORD"]
server = config["POSTGRES_SERVER"]
database = config["POSTGRES_DATABASE"]

engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{server}/{database}"
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 