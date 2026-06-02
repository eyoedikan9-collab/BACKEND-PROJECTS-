from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
from dotenv import dotenv_values
# from sqlalchemy.orm import sessionmaker

load_dotenv()
config = dotenv_values(".env")
user = config["POSTGRES_USER"]
password = config["POSTGRES_PASSWORD"]
server = config["POSTGRES_SERVER"]
database = config["POSTGRES_DATABASE"]

# DATABASE_URL = "sqlite:///./todo.db"

# engine = create_engine(DATABASE_URL)

engine = create_async_engine(
    f"postgresql+asyncpg://{user}:{password}@{server}/{database}"
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

        
    # db = AsyncSessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close() 