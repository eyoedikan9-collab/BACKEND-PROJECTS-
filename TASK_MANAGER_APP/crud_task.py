from sqlalchemy.orm import Session
from database import engine
from models_task import User, Tasks
from sqlalchemy import select

session = Session(engine)

# phillip = User(first_name="Phillip", last_name="Edikan", email="Philliped@gmail.com", gender="male", age= 32)
# session.add(phillip)
# session.commit()


# phillip_task = Tasks(task="Going to the market", user_id="1", date_time="2026-03-24 22:15:30", duration="2 hours")
# session.add(phillip_task)
# session.commit()

some_phillip = session.get(User, 1)
print(some_phillip)

# n = session.get(User, 2)
# session.delete(n)