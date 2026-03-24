from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass

from database import engine
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import String, ForeignKey

class User(Base):
    __tablename__ = "task_users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str]
    gender:  Mapped[str] = mapped_column(String(20))
    age: Mapped[int]

    task: Mapped[List["Tasks"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r}, first_name={self.first_name!r}, last_name={self.last_name!r}, email={self.email!r}, gender={self.gender!r}, age={self.age!r})"
    
class Tasks(Base):
    __tablename__ = "task_details"
    task_id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str]
    user_id = mapped_column(ForeignKey("task_users.user_id"))
    date_time: Mapped[str] = mapped_column(String(20))
    duration: Mapped[str] = mapped_column(String(20))


    user: Mapped[User] = relationship(back_populates="task")
    def __repr__(self) -> str:
        return f"Tasks(task_id={self.task_id!r}, task={self.task!r}, date_time={self.date_time!r}, duration={self.duration!r})"


Base.metadata.create_all(engine)

