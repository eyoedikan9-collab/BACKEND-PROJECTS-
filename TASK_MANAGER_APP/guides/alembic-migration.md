# Alembic Migration Guide: Learn by Doing

> A task-based guide for learning database migrations with Alembic and SQLAlchemy.

---

## Prerequisites

Before starting, make sure you have:

- Python 3.8+ installed
- Basic understanding of Python and SQL
- PostgreSQL or SQLite available
- `pip` working in your terminal

---

## Setup

Install the required packages:

```bash
pip install alembic sqlalchemy psycopg2-binary
```

Create a project folder:

```bash
mkdir alembic-learning && cd alembic-learning
```

---

## Task 1: Initialize Alembic in a Project

**Goal:** Set up Alembic so it knows where your database is and where to store migrations.

### Step 1 — Initialize

```bash
alembic init migrations
```

This creates:

```
alembic-learning/
├── alembic.ini          ← main config file
└── migrations/
    ├── env.py           ← tells Alembic how to connect to your DB
    ├── script.py.mako   ← template for new migration files
    └── versions/        ← your migration files will live here
```

### Step 2 — Configure your database URL

Open `alembic.ini` and find this line:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

Replace it with your actual database URL. For SQLite (easiest to start):

```ini
sqlalchemy.url = sqlite:///./myapp.db
```

For PostgreSQL:

```ini
sqlalchemy.url = postgresql://postgres:password@localhost:5432/myapp
```

### Step 3 — Verify

```bash
alembic current
```

Expected output:

```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
(no current revision)
```

No errors means Alembic can reach your database. ✅

---

## Task 2: Create Your First Table with a Migration

**Goal:** Create a `users` table using Alembic, without writing raw SQL by hand.

### Step 1 — Generate a migration file

```bash
alembic revision -m "create users table"
```

This creates a file inside `migrations/versions/` with a name like:

```
a1b2c3d4e5f6_create_users_table.py
```

### Step 2 — Write the migration

Open the generated file. You'll see two empty functions: `upgrade()` and `downgrade()`.

Fill them in:

```python
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('users')
```

**Key concept:**
- `upgrade()` → what happens when you apply this migration (moving forward)
- `downgrade()` → how to undo it (rolling back)

### Step 3 — Apply the migration

```bash
alembic upgrade head
```

`head` means "apply all migrations up to the latest one."

### Step 4 — Confirm it worked

```bash
alembic current
```

You should now see your migration's revision ID printed, meaning the DB is at that version.

---

## Task 3: Add a Column to an Existing Table

**Goal:** Add a `phone_number` column to the `users` table after it already exists in production. This is the most common real-world migration scenario.

### Step 1 — Generate a new migration

```bash
alembic revision -m "add phone number to users"
```

### Step 2 — Write the migration

```python
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'users',
        sa.Column('phone_number', sa.String(20), nullable=True)
    )


def downgrade():
    op.drop_column('users', 'phone_number')
```

> **Why `nullable=True`?**  
> Existing rows have no `phone_number` value. If you set `nullable=False` without a default, the migration will fail because the DB can't populate the existing rows. Always add new columns as nullable unless you provide a `server_default`.

### Step 3 — Apply it

```bash
alembic upgrade head
```

### Step 4 — Check the migration history

```bash
alembic history
```

Output:

```
a1b2c3d4e5f6 -> b2c3d4e5f6a1 (head), add phone number to users
<base> -> a1b2c3d4e5f6, create users table
```

Each migration has a parent, forming a chain. This is how Alembic knows the order to apply them.

---

## Task 4: Roll Back a Migration

**Goal:** Undo a migration that caused a problem. This is your safety net.

### Scenario

You just deployed the `add phone number to users` migration and it broke something. You need to roll it back immediately.

### Step 1 — Check current state

```bash
alembic current
```

You'll see the latest revision ID (e.g., `b2c3d4e5f6a1`).

### Step 2 — Roll back one step

```bash
alembic downgrade -1
```

The `-1` means "go back one revision." Alembic calls the `downgrade()` function in your migration file, which drops the `phone_number` column.

### Step 3 — Confirm rollback

```bash
alembic current
```

You should now see the previous revision ID (`a1b2c3d4e5f6`), meaning you're back to just the `users` table without the phone column.

### Going back further

```bash
alembic downgrade -2    # go back 2 revisions
alembic downgrade base  # roll ALL the way back (drops everything)
```

> **Real talk:** In production, always test your `downgrade()` function locally before deploying. A broken rollback is worse than a broken migration.

---

## Task 5: Auto-generate Migrations from SQLAlchemy Models

**Goal:** Let Alembic compare your Python models to the real database and automatically generate the migration for you — instead of writing it by hand.

This is how professional teams work.

### Step 1 — Define your models

Create a file called `models.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)  # NEW column


class Post(Base):
    __tablename__ = 'posts'  # NEW table

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    body = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
```

### Step 2 — Connect models to Alembic

Open `migrations/env.py`. Find this line:

```python
target_metadata = None
```

Replace it with:

```python
from models import Base
target_metadata = Base.metadata
```

### Step 3 — Auto-generate the migration

```bash
alembic revision --autogenerate -m "add is_active to users and create posts table"
```

Alembic will compare your models to the actual DB and generate:

```python
def upgrade():
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
    )
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('users', 'is_active')
    op.drop_table('posts')
```

### Step 4 — Review before applying

**Always read the generated migration before running it.** Autogenerate is good but not perfect — it can miss some changes (like server defaults or custom types) and sometimes includes things you didn't intend.

### Step 5 — Apply

```bash
alembic upgrade head
```

---

## Quick Reference

| Command | What it does |
|---|---|
| `alembic init <folder>` | Set up Alembic in your project |
| `alembic revision -m "message"` | Create a blank migration file |
| `alembic revision --autogenerate -m "message"` | Generate migration from model diff |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic upgrade +1` | Apply one migration forward |
| `alembic downgrade -1` | Roll back one migration |
| `alembic downgrade base` | Roll back everything |
| `alembic current` | Show current DB revision |
| `alembic history` | Show full migration chain |

---

## Common Mistakes to Avoid

**1. Editing a migration after it's been applied**  
Once a migration is in your DB and committed to Git, treat it as read-only. Create a new migration to fix it instead.

**2. Skipping `downgrade()`**  
Leaving `downgrade()` empty (`pass`) means you can never roll back. Always write it.

**3. Nullable columns without a plan**  
Adding a `nullable=False` column to a table with existing data will fail. Either add it as `nullable=True` first, backfill the data, then add a `NOT NULL` constraint in a second migration.

**4. Not committing migration files to Git**  
Migration files belong in version control alongside your code. The DB version and the code version should always match.

