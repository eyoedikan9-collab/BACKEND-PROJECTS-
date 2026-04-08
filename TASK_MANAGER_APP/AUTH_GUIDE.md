# Authentication & Authorization — Task Manager App

## What You're Building

Right now your API lets anyone create users and tasks with no restrictions.
By the end of this guide:

- Passwords are stored **hashed** (never plain text)
- Users **log in** and receive a **JWT token**
- Task routes are **protected** — you must be logged in to use them
- Users can **only access their own tasks** (authorization)

---

## Concepts First

### Authentication vs Authorization

| Term | Question it answers | Example |
|---|---|---|
| **Authentication** | Who are you? | "I am user #5, here's my token" |
| **Authorization** | What are you allowed to do? | "User #5 can only see their own tasks" |

Both are needed. A valid token proves identity (authn). Checking ownership enforces permissions (authz).

### Why JWT instead of sessions?

Session-based auth stores state on the server — the server has to remember who is logged in.
**JWT (JSON Web Token)** is stateless — the token itself contains the user info, signed by the server. The server just verifies the signature on each request. This is the standard approach for REST APIs.

### What a JWT looks like

A JWT has three parts separated by dots:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1In0.abc123xyz
     HEADER                PAYLOAD       SIGNATURE
```

- **Header** — which algorithm was used to sign
- **Payload** — the claims (e.g. `{"sub": "5"}` — the user's ID)
- **Signature** — proves the token hasn't been tampered with

The payload is **base64-encoded, not encrypted** — anyone can decode it. Never put sensitive data in a JWT. The signature is what makes it trustworthy.

---

## Task 1 — Install Dependencies

```bash
pip install "pwdlib[bcrypt]" "python-jose[cryptography]"
```

- `pwdlib` — password hashing library (modern replacement for passlib)
- `python-jose` — for creating and verifying JWTs

Confirm:

```bash
pip show pwdlib python-jose
```

**Checkpoint:** Both packages show a version number.

---

## Task 2 — Update the User Model and Schemas

### In `models_task.py`

Add a `hashed_password` column to the `User` class:

```python
hashed_password: Mapped[str]
```

Then re-run `Base.metadata.create_all(engine)` (already at the bottom of the file) — but since the table already exists, you'll need to **drop and recreate** it or add the column manually.

The easiest approach for now: connect to your database and run:

```sql
ALTER TABLE task_users ADD COLUMN hashed_password VARCHAR NOT NULL DEFAULT '';
```

### In `schema.py`

`UserCreate` needs a `password` field (plain text — you'll hash it before saving):

```python
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: str
    age: int
    password: str       # add this
```

`UserPublic` must **never** include the password or hash. Check yours — it should only have `user_id`, `first_name`, `last_name`, and `email`. That's correct as-is.

Add one new schema for the login response:

```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

**Checkpoint:** `schema.py` has `UserCreate` with `password`, `UserPublic` without it, and a new `Token` schema.

---

## Task 3 — Create `auth.py`

Create a new file `auth.py`. This is where all authentication logic lives — separate from your routes and CRUD.

```python
from pwdlib import PasswordHash
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

SECRET_KEY = "change-this-to-a-long-random-string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
```

**Your job:** implement these three functions.

```python
def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the plain text password."""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored hash."""
    pass


def create_access_token(data: dict) -> str:
    """
    Take a dict of claims (e.g. {"sub": "5"}), add an expiry time,
    sign it with SECRET_KEY, and return the JWT string.
    """
    pass
```

**Hints:**

- `password_hash.hash("mypassword")` — returns the hashed string
- `password_hash.verify("mypassword", "$2b$12$...")` — returns `True` or `False`
- For the JWT, copy `data` into a new dict, add `"exp"` as a `datetime` object (use `datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)`), then call `jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)`

**Checkpoint:** In a Python shell, import `auth` and confirm:

```python
h = auth.hash_password("hello")
print(h)                                # should look like $2b$12$...
print(auth.verify_password("hello", h)) # True
print(auth.verify_password("wrong", h)) # False
```

---

## Task 4 — Hash the Password in `crud_task.py`

`create_user` currently does `User(**user.model_dump())` — this would try to set a `password` field on the ORM model, which doesn't exist. You need to hash the password and store it in `hashed_password` instead.

**Your job:** Update `create_user` so that:

1. It extracts the plain password from the schema
2. Hashes it using `auth.hash_password`
3. Creates the `User` ORM object with `hashed_password` set correctly (and no `password` field)

**Hint:** `user.model_dump()` includes `password`. You can remove a key from a dict with `del d["key"]` or use `user.model_dump(exclude={"password"})`.

Also add a new function:

```python
def get_user_by_email(db: Session, email: str) -> User | None:
    """Look up a user by email address. Return None if not found."""
    pass
```

You'll need this for login — users identify themselves by email, not ID.

**Checkpoint:** Create a user via `/docs`. Check your database — `hashed_password` should contain a bcrypt hash, not the plain text password.

---

## Task 5 — Add the Login Endpoint

In `main.py`, add this import at the top:

```python
from fastapi.security import OAuth2PasswordRequestForm
from schema import Token
import auth
```

Then add the login route. `OAuth2PasswordRequestForm` is a FastAPI built-in that reads `username` and `password` from a form submission (the OAuth2 standard uses `username` as the field name — you'll use it as the email):

```python
@app.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    pass
```

**Your job:** implement the body. It should:

1. Look up the user by `form_data.username` (treated as email) using `crud_task.get_user_by_email`
2. If no user found, or if `auth.verify_password(form_data.password, user.hashed_password)` is False — raise an `HTTPException(status_code=401, detail="Invalid credentials")`
3. Call `auth.create_access_token({"sub": str(user.user_id)})` to create a token
4. Return `{"access_token": token, "token_type": "bearer"}`

**Checkpoint:** Go to `/docs`, use `POST /auth/token`, enter your user's email as `username` and their password. You should get back a JSON object with `access_token`.

---

## Task 6 — Protect Routes with `get_current_user`

Add this to `auth.py`:

```python
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
```

Then implement this dependency function:

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decode the JWT, extract the user_id from the 'sub' claim,
    fetch the user from the database, and return them.
    Raise 401 if the token is invalid or the user doesn't exist.
    """
    pass
```

**Hints:**

- Decode with `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])` — wrap in try/except for `JWTError`
- The payload is a dict — get the user ID with `payload.get("sub")`
- `get_db` is in `database.py` — import it in `auth.py`
- If anything goes wrong, raise: `HTTPException(status_code=401, detail="Could not validate credentials")`

**Your job:** Now update your task routes in `main.py` to require authentication. Add `current_user = Depends(auth.get_current_user)` to each task route's parameters:

```python
@app.post("/users/{user_id}/tasks", response_model=TaskPublic)
def create_task(user_id: int, task: TaskCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    pass  # your existing logic here
```

Do the same for `GET /users/{user_id}/tasks`.

**Checkpoint:** Try calling `GET /users/1/tasks` without a token — you should get a **401**. Click the **Authorize** button in `/docs`, enter your token, then try again — you should get a **200**.

---

## Task 7 — Authorization: Users Can Only See Their Own Tasks

Authentication confirms *who you are*. Now enforce *what you can do*.

A logged-in user should not be able to read or create tasks for a different user.

**Your job:** At the start of each task route body, add an ownership check:

```python
if current_user.user_id != user_id:
    raise HTTPException(status_code=403, detail="Not authorized to access this user's tasks")
```

**What's the difference between 401 and 403?**

| Code | Meaning |
|---|---|
| 401 Unauthorized | You haven't proven who you are (no token / bad token) |
| 403 Forbidden | We know who you are, but you're not allowed to do this |

**Checkpoint:** Log in as user #1. Try `GET /users/2/tasks` — you should get a **403**. Try `GET /users/1/tasks` — you should get a **200**.

---

## Task 8 — Test the Full Flow

Run through this checklist end to end using `/docs`:

- [ ] `POST /users` — create a new user with a password
- [ ] Check the DB — `hashed_password` is a bcrypt hash, not plain text
- [ ] `POST /auth/token` — log in with that user's email and password, get a token
- [ ] Click **Authorize** in `/docs` and paste the token
- [ ] `POST /users/{user_id}/tasks` — create a task (authenticated)
- [ ] `GET /users/{user_id}/tasks` — retrieve tasks (authenticated)
- [ ] Try the same routes **without** a token — confirm you get **401**
- [ ] Log in as user #1, try `GET /users/2/tasks` — confirm **403**

---

## Stretch Task — Token Expiry

Your tokens already include an `exp` claim. Let's see it in action.

1. In `auth.py`, change `ACCESS_TOKEN_EXPIRE_MINUTES = 30` to `ACCESS_TOKEN_EXPIRE_MINUTES = 0` (expires immediately)
2. Log in, copy the token, wait a moment, then try a protected route
3. What error do you get? Where does it come from?
4. Update your `get_current_user` to return a clear `401` with `"Token has expired"` as the detail when this happens

**Hint:** `python-jose` raises `jose.ExpiredSignatureError` (a subclass of `JWTError`) when the token is expired. You can catch it separately before catching the general `JWTError`.

---

## Final File Structure

```
TASK_MANAGER_APP/
├── .env
├── database.py        # engine + get_db()
├── models_task.py     # User model now has hashed_password
├── schema.py          # UserCreate has password field, new Token schema
├── crud_task.py       # create_user hashes password, new get_user_by_email
├── auth.py            # hash/verify, JWT create/decode, get_current_user dependency
└── main.py            # login route + protected task routes
```

---

## Quick Reference

| What you want | How to do it |
|---|---|
| Hash a password | `password_hash.hash("plain")` |
| Verify a password | `password_hash.verify("plain", "hashed")` |
| Create a JWT | `jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)` |
| Decode a JWT | `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])` |
| Require login on a route | `current_user = Depends(auth.get_current_user)` |
| Read form login data | `form_data: OAuth2PasswordRequestForm = Depends()` |
| Token not provided → | 401 Unauthorized |
| Token valid but wrong user → | 403 Forbidden |
