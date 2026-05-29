# Async Transition Guide — Task Manager App

This guide walks you through converting the Task Manager App from synchronous to
fully asynchronous. Every step is grounded in **your actual code**.

---

## Why Bother With Async?

FastAPI runs on an ASGI server (Uvicorn). When your route handlers are plain `def`
functions, FastAPI runs each one in a **thread pool** — it still works, but it's
wasteful. When you switch to `async def`, FastAPI runs them directly on the event
loop, which means:

- Database calls don't block other requests while waiting for I/O
- You can handle many more concurrent connections with fewer threads
- The code better reflects how FastAPI is designed to be used

---

## What Needs to Change (Overview)

| File | Change |
|---|---|
| `requirements.txt` | Add async DB driver (`aiosqlite` or `asyncpg`) |
| `database.py` | Swap sync engine/session for async equivalents |
| `routes.py` | Add `async def` + `await` to every function |
| `crud_task.py` | Same as routes.py (consolidate later) |
| `auth.py` | Make `get_current_user` and `get_current_admin_user` async |
| `main.py` | Add `async def` to every route handler |

---

## Step 1 — Update Dependencies

You need an async-compatible database driver. The sync `psycopg2` and raw SQLite
cannot be used with `AsyncSession`.

**For SQLite (dev/learning):** add `aiosqlite`
**For PostgreSQL (production):** add `asyncpg`, remove `psycopg2`

```
# requirements.txt additions
aiosqlite==0.21.0      # async SQLite driver
asyncpg==0.30.0        # async PostgreSQL driver (use instead of psycopg2)
```

Install:
```bash
pip install aiosqlite asyncpg
```

---

## Step 2 — Rewrite `database.py`

**Current code:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**New async version:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Note: sqlite+aiosqlite:// prefix tells SQLAlchemy to use the async driver
DATABASE_URL = "sqlite+aiosqlite:///./todo.db"

# For PostgreSQL it would be:
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/taskmanager"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # important for async: avoids lazy-load issues
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Key differences:
- `create_async_engine` instead of `create_engine`
- `async_sessionmaker` instead of `sessionmaker`
- `get_db` is now an `async` generator using `async with`
- `expire_on_commit=False` prevents SQLAlchemy from expiring objects after commit
  (lazy loading doesn't work in async — you'd get a `MissingGreenlet` error)

---

## Step 3 — Update the Query Style in `routes.py`

SQLAlchemy's legacy `db.query()` style does **not** work with `AsyncSession`.
You must use the `select()` statement style from SQLAlchemy 2.0.

**The pattern change:**

| Old (sync) | New (async) |
|---|---|
| `db.query(User).filter(...).first()` | `(await db.execute(select(User).where(...))).scalars().first()` |
| `db.query(User).all()` | `(await db.execute(select(User))).scalars().all()` |
| `db.add(obj)` | `db.add(obj)` (same) |
| `db.commit()` | `await db.commit()` |
| `db.refresh(obj)` | `await db.refresh(obj)` |
| `db.delete(obj)` | `await db.delete(obj)` |
| `db.get(User, id)` | `await db.get(User, id)` |

**Rewritten `routes.py`:**
```python
from schema import TaskCreate, TaskPublic, UserCreate, UserPublic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, Tasks
from auth import hash_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    plain_password = user.password
    hashed_password = hash_password(plain_password)
    user_data = user.model_dump(exclude={"password"})
    user_stored = User(**user_data, hashed_password=hashed_password)
    db.add(user_stored)
    await db.commit()
    await db.refresh(user_stored)
    return user_stored


async def create_task(db: AsyncSession, task: TaskCreate, user_id: int) -> TaskPublic:
    task_data = task.model_dump()
    new_task = Tasks(**task_data, user_id=user_id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return TaskPublic.model_validate(new_task)


async def get_all_users(db: AsyncSession, offset: int = 0, limit: int = 10) -> list[User]:
    result = await db.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_tasks_for_user(db: AsyncSession, user_id: int) -> list[Tasks]:
    result = await db.execute(select(Tasks).where(Tasks.user_id == user_id))
    return result.scalars().all()


async def delete_user(db: AsyncSession, user_id: int) -> User | None:
    user = await db.get(User, user_id)
    if user:
        await db.delete(user)
        await db.commit()
    return user


async def update_role(db: AsyncSession, user_id: int, role: str) -> User:
    user = await db.get(User, user_id)
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user
```

---

## Step 4 — Update `auth.py`

`get_current_user` queries the database, so it must become async. Once it's async,
`get_current_admin_user` — which depends on it — also needs updating.

**Current `get_current_user` (sync):**
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    ...
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    ...
```

**New async version:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserPublic:
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
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.user_id == int(user_id)))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return UserPublic.model_validate(user)
```

**Current `get_current_admin_user` has a bug** on line 85:
```python
# WRONG — this is a tuple, not Annotated usage
def get_current_admin_user(current_user: Annotated[(User, Depends(get_current_user))]):
```

**Fixed async version:**
```python
async def get_current_admin_user(
    current_user: Annotated[UserPublic, Depends(get_current_user)]
) -> UserPublic:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

Note: `401` was changed to `403` — 401 means "not authenticated", 403 means "authenticated
but not authorized". An admin check is a 403.

---

## Step 5 — Update Route Handlers in `main.py`

All route handlers need `async def`. The dependency injection (`Depends`) handles
async functions automatically — FastAPI awaits them for you.

**Replace every `def` route with `async def`:**

```python
# Before
@app.post("/auth/refresh")
def refresh(token: RefreshTokenRequest, db: Session = Depends(get_db)):
    ...

# After
@app.post("/auth/refresh")
async def refresh(token: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    ...
```

The same two rules apply to every route: `async def`, and `await` every DB call.
See Step 7 for worked examples.

---

## Step 6 — Table Creation at Startup

Currently `models.py` calls `Base.metadata.create_all(engine)` at import time.
With async, engine operations also need to be async. Use the `lifespan` pattern
(the `on_event` decorator is deprecated in modern FastAPI).

**Add a lifespan function to `main.py`:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine
from models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # create_all is synchronous. run_sync() runs it inside the async
        # connection without blocking the event loop — equivalent to
        # Base.metadata.create_all(conn) but async-safe.
        await conn.run_sync(Base.metadata.create_all)
    yield  # app runs here; anything after yield runs on shutdown
    await engine.dispose()  # close all connections in the pool cleanly

app = FastAPI(title="Todo app", lifespan=lifespan)
```

Then remove any `create_all` calls from `models.py`.

---

---

## Step 7 — Route Handler Examples

Two examples are shown. Apply the same pattern to every other route yourself.

### Example A — GET with authentication

```python
# BEFORE
@app.get("/tasks", response_model=List[TaskPublic])
def get_tasks(db: Session = Depends(get_db), current_user: UserPublic = Depends(auth.get_current_user)):
    tasks = get_tasks_for_user(db=db, user_id=current_user.user_id)
    return tasks

# AFTER
@app.get("/tasks", response_model=List[TaskPublic])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: UserPublic = Depends(auth.get_current_user)
):
    tasks = await get_tasks_for_user(db=db, user_id=current_user.user_id)
    return tasks
```

What changed:
- `def` → `async def`
- `Session` → `AsyncSession`
- `get_tasks_for_user(...)` → `await get_tasks_for_user(...)`
- FastAPI awaits `get_current_user` automatically because it's now also async

### Example B — POST with a 404 guard

```python
# BEFORE
@app.get("/user/{user_id}", response_model=UserPublic)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    a_user = get_user(db=db, user_id=user_id)
    if not a_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
    return a_user

# AFTER
@app.get("/user/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserPublic = Depends(get_current_admin_user)
):
    a_user = await get_user(db=db, user_id=user_id)
    if not a_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
    return a_user
```

The rule is simple: **every call to a function that touches the database needs `await`.**
Raising `HTTPException` is not a DB call — no `await` there.

---

## Common Errors You Will Hit

### `MissingGreenlet: greenlet_spawn has not been called`
Caused by accessing an ORM relationship or expired attribute after the session closes.
Fix: set `expire_on_commit=False` in `async_sessionmaker` (done in Step 2), and avoid
accessing lazy-loaded relationships without an `await`.

### `sqlalchemy.exc.MissingGreenlet` on `db.query()`
You used the legacy `db.query()` style with `AsyncSession`. Switch to `select()` as
shown in Step 3.

### `TypeError: object Session can't be used in 'await' expression`
You're passing a sync `Session` where an `AsyncSession` is expected, or the `get_db`
function is still the sync version. Make sure `database.py` is fully updated.

### Route returns empty/expired objects
Missing `expire_on_commit=False` or you're accessing attributes after `db.commit()`
without a `db.refresh()`. Always `await db.refresh(obj)` after committing if you
return the object.

---

## Migration Checklist

- [ ] `pip install aiosqlite asyncpg`
- [ ] Update `requirements.txt`
- [ ] Rewrite `database.py` with `create_async_engine` and `async_sessionmaker`
- [ ] Rewrite all functions in `routes.py` as `async def` with `await`
- [ ] Update `auth.py`: make `get_current_user` and `get_current_admin_user` async, fix the `Annotated` bug
- [ ] Update `main.py`: all routes become `async def`, all CRUD calls get `await`
- [ ] Add `startup` event to `main.py` for table creation
- [ ] Remove `crud_task.py` (it's a leftover scratch file) or consolidate into `routes.py`
- [ ] Test every endpoint with Swagger UI at `http://127.0.0.1:8080/docs`

---
