# SQLAlchemy Integration — Task Manager App

## What You're Starting With

Your project already has three files set up:

| File | What it does |
|---|---|
| `database.py` | Creates the database engine and a `get_db()` session factory |
| `models_task.py` | Defines the `User` and `Tasks` tables as Python classes |
| `schema.py` | Defines Pydantic schemas for validating input/output data |

Your job across these tasks is to:
1. Write the CRUD functions that talk to the database
2. Build a FastAPI app that exposes those functions as API endpoints

---

## Task 1 — Install Dependencies

Before writing any code, make sure you have everything installed.

```bash
pip install fastapi uvicorn[standard]
```

SQLAlchemy, psycopg2, and pydantic should already be installed from earlier. Confirm with:

```bash
pip show fastapi sqlalchemy pydantic
```

**Checkpoint:** All three packages show a version number. No errors.

---

## Task 2 — Write CRUD Functions in `crud_task.py`

Open `crud_task.py`. The test/scratch code in there was just for exploring — now you'll replace it with proper functions.

Each function should accept a `db: Session` as its first parameter. This is how the session gets passed in from the API layer.

**Your job:** Implement the following functions. Do not hardcode any values.

```python
from sqlalchemy.orm import Session
from models_task import User, Tasks
from schema import UserCreate, TaskCreate


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user and save to the database."""
    pass  # your code here


def get_user(db: Session, user_id: int) -> User | None:
    """Retrieve a single user by their ID. Return None if not found."""
    pass


def get_all_users(db: Session) -> list[User]:
    """Return all users in the database."""
    pass


def create_task(db: Session, task: TaskCreate, user_id: int) -> Tasks:
    """Create a new task assigned to a specific user."""
    pass


def get_tasks_for_user(db: Session, user_id: int) -> list[Tasks]:
    """Return all tasks belonging to a specific user."""
    pass
```

**Hints:**
- To save a new record: `db.add(obj)` → `db.commit()` → `db.refresh(obj)` → `return obj`
- To look up by primary key: `db.get(ModelClass, id)`
- To get all rows: `db.query(ModelClass).all()`
- To filter: `db.query(ModelClass).filter(ModelClass.column == value).all()`
- Pydantic models have a `.model_dump()` method that returns a dict — useful for unpacking into a model constructor

**Checkpoint:** Add a quick manual test at the bottom of the file (inside `if __name__ == "__main__":`) to call `create_user` with a real session and print the result. Run the file directly to confirm it works before moving on.

---

## Task 3 — Create `main.py`

Create a new file called `main.py` in the same folder. This is where your FastAPI application lives.

Start with this boilerplate:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud_task
from schema import UserCreate, UserPublic, TaskCreate, TaskPublic

app = FastAPI()
```

**Your job:** Add four routes to the app. The route signatures are given — you write the body of each one.

---

### Route 1 — Create a User

```python
@app.post("/users", response_model=UserPublic)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    pass
```

Call the matching function from `crud_task` and return the result.

---

### Route 2 — Get a Single User

```python
@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int, db: Session = Depends(get_db)):
    pass
```

If the user is not found, raise: `HTTPException(status_code=404, detail="User not found")`

---

### Route 3 — Create a Task for a User

```python
@app.post("/users/{user_id}/tasks", response_model=TaskPublic)
def create_task(user_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    pass
```

First check that the user exists. If not, raise a 404.

---

### Route 4 — Get All Tasks for a User

```python
@app.get("/users/{user_id}/tasks", response_model=list[TaskPublic])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    pass
```

**What is `Depends(get_db)`?**
FastAPI's dependency injection system. It automatically calls `get_db()` before your route runs, passes the session in, and closes it when the request is done. You don't call `get_db()` yourself.

**Checkpoint:** Start your server:
```bash
uvicorn main:app --reload
```
It should start without errors. Visit `http://127.0.0.1:8000/docs` to see the auto-generated API documentation.

---

## Task 4 — Fix Schema Serialization

Try using the `/docs` page to create a user. You'll likely see a serialization error. Here's why:

FastAPI needs to convert a SQLAlchemy ORM object into JSON. Pydantic doesn't know how to read ORM object attributes by default — it expects a dictionary.

**Your job:** Add one line to each of your `Public` schemas in `schema.py`:

```python
from pydantic import BaseModel, ConfigDict

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    first_name: str
    # ... rest of fields
```

Do the same for `TaskPublic`.

**Why does this fix it?** `from_attributes=True` tells Pydantic to read values from object attributes (like `user.first_name`) instead of dictionary keys (like `user["first_name"]`).

**Checkpoint:** Create a user via `/docs`. You should get back a JSON response with `user_id`, `first_name`, `last_name`, and `email`.

---

## Task 5 — Test All Endpoints

Using the interactive docs at `http://127.0.0.1:8000/docs`, run through this checklist:

- [ ] `POST /users` — create a new user, confirm you get a 200 with user data
- [ ] `GET /users/{user_id}` — retrieve the user you just created
- [ ] `GET /users/9999` — confirm you get a **404**, not a 500 error
- [ ] `POST /users/{user_id}/tasks` — create a task for your user
- [ ] `GET /users/{user_id}/tasks` — confirm the task appears in the list

**Checkpoint:** All 5 pass with correct status codes and response data.

---

## Stretch Task — Delete a Task

Add a delete endpoint:

```
DELETE /users/{user_id}/tasks/{task_id}
```

- Return `{"message": "Task deleted"}` on success
- Raise a 404 if the task doesn't exist
- You'll need a new function in `crud_task.py` and a new route in `main.py`

Hint: `db.delete(obj)` → `db.commit()`

---

## Final File Structure

```
TASK_MANAGER_APP/
├── .env
├── database.py        # engine + get_db() — already done
├── models_task.py     # ORM models — already done
├── schema.py          # Pydantic schemas — updated in Task 4
├── crud_task.py       # CRUD functions — written in Task 2
└── main.py            # FastAPI app + routes — written in Task 3
```

---

## Quick Reference

| What you want to do | How to do it |
|---|---|
| Save a new record | `db.add(obj)` → `db.commit()` → `db.refresh(obj)` |
| Find one record by ID | `db.get(ModelClass, id)` |
| Get all records | `db.query(ModelClass).all()` |
| Filter records | `db.query(ModelClass).filter(ModelClass.field == value).all()` |
| Delete a record | `db.delete(obj)` → `db.commit()` |
| Inject session in FastAPI | `db: Session = Depends(get_db)` |
| Make Pydantic work with ORM | `model_config = ConfigDict(from_attributes=True)` |
