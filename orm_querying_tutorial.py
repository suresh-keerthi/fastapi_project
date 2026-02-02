"""
SQLALCHEMY ORM QUERYING & CRUD — COMPLETE GUIDE
===============================================

This file covers EVERYTHING about querying and CRUD operations:
• Create (INSERT) operations
• Read (SELECT) operations with filters, sorting, pagination
• Update operations
• Delete operations
• Transactions (commit, rollback, savepoints)
• Aggregation and grouping
• Subqueries and CTEs
• Common pitfalls and best practices
• Performance optimization tips
"""

from sqlalchemy import (
    create_engine,
    select,
    insert,
    update,
    delete,
    and_,
    or_,
    not_,
    func,
    distinct,
    case,
    cast,
    text,
    literal_column,
    exists,
    union,
    union_all,
    desc,
    asc,
    nullsfirst,
    nullslast,
)
from sqlalchemy.orm import (
    Session,
    sessionmaker,
    joinedload,
    selectinload,
    lazyload,
    noload,
    contains_eager,
    aliased,
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Any
import random

from orm_models_tutorial import Base, CompleteUser
from orm_relationships_tutorial import Author, Book, Department, Employee


# ============================================================
# 0️⃣ SETUP — CREATE ENGINE AND SESSION
# ============================================================
"""
Before we can query, we need:
1. Engine (connection to database)
2. Session (workspace for operations)
"""

engine = create_engine(
    "postgresql+psycopg2://postgres:1729@localhost:5432/newdb",
    echo=False,  # Set to True to see SQL
)

SessionLocal = sessionmaker(bind=engine)


# ============================================================
# 1️⃣ CREATE OPERATIONS — INSERT
# ============================================================
"""
Three ways to create records:
1. Instantiate model → add() → commit()
2. Using insert() statement (bulk operations)
3. session.execute(insert()) with ORM
"""


def create_single_record():
    """Method 1: Create one record (most common)"""

    with SessionLocal() as session:
        # Create instance (NOT in database yet!)
        user = CompleteUser(
            username="alice", email="alice@example.com", password="securepass123"
        )

        # Add to session (still NOT in database!)
        session.add(user)

        # At this point:
        # - user.id is None (not generated yet)
        # - No SQL has been sent to database

        # Commit (NOW it goes to database!)
        session.commit()

        # After commit:
        # - user.id is populated (auto-increment)
        # - Record exists in database

        print(f"Created user with ID: {user.id}")
        return user.id


def create_multiple_records():
    """Method 1b: Create multiple records"""

    with SessionLocal() as session:
        users = [
            CompleteUser(username="bob", email="bob@example.com", password="pass123"),
            CompleteUser(
                username="charlie", email="charlie@example.com", password="pass456"
            ),
            CompleteUser(
                username="diana", email="diana@example.com", password="pass789"
            ),
        ]

        # Add all at once
        session.add_all(users)

        # All users still have id=None here

        session.commit()

        # Now all have IDs
        for user in users:
            print(f"Created: {user.username} (ID: {user.id})")


def create_with_relationships():
    """Create parent and children together"""

    with SessionLocal() as session:
        # Create author
        author = Author(name="J.K. Rowling")

        # Create books (children)
        book1 = Book(title="Harry Potter 1")
        book2 = Book(title="Harry Potter 2")

        # Link them (Python-side only)
        author.books = [book1, book2]

        # Add just the parent (children auto-added due to cascade)
        session.add(author)

        session.commit()

        print(f"Created author: {author.name}")
        print(f"With books: {[b.title for b in author.books]}")


def bulk_insert():
    """Method 2: Bulk insert (faster for many records)"""

    with SessionLocal() as session:
        # Prepare data as dictionaries
        users_data = [
            {
                "username": f"user_{i}",
                "email": f"user_{i}@test.com",
                "password_hash": f"hash{i}",
            }
            for i in range(100, 110)
        ]

        # Bulk insert - one SQL statement for all
        session.execute(insert(CompleteUser), users_data)

        session.commit()
        print(f"Bulk inserted {len(users_data)} users")


def insert_with_defaults():
    """Understanding defaults during insert"""

    with SessionLocal() as session:
        # Only providing required fields
        # Other fields use defaults
        user = CompleteUser(
            username="minimal",
            email="minimal@test.com",
            password="password123",
            # is_active defaults to True
            # email_verified defaults to False
            # created_at uses Python default
            # updated_at uses Python default
        )

        session.add(user)
        session.commit()

        print(f"is_active: {user.is_active}")  # True (default)
        print(f"email_verified: {user.email_verified}")  # False (default)
        print(f"created_at: {user.created_at}")  # Current timestamp


# ============================================================
# 2️⃣ READ OPERATIONS — SELECT (THE BASICS)
# ============================================================
"""
SELECT operations retrieve data from the database.
SQLAlchemy 2.0 uses select() instead of Query.
"""


def select_all_records():
    """Get all records from a table"""

    with SessionLocal() as session:
        # Build the query
        stmt = select(CompleteUser)

        # Execute and get results
        result = session.execute(stmt)

        # scalars() extracts the objects from result rows
        users = result.scalars().all()

        print(f"Found {len(users)} users")
        for user in users:
            print(f"  - {user.username} ({user.email})")

        return users


def select_specific_columns():
    """Get only specific columns (more efficient)"""

    with SessionLocal() as session:
        # Select specific columns only
        stmt = select(CompleteUser.username, CompleteUser.email)

        result = session.execute(stmt)

        # Returns tuples, not objects
        for username, email in result:
            print(f"User: {username}, Email: {email}")


def select_first_record():
    """Get just the first record"""

    with SessionLocal() as session:
        # Method 1: Using limit
        stmt = select(CompleteUser).limit(1)
        user = session.execute(stmt).scalar_one_or_none()

        if user:
            print(f"First user: {user.username}")

        # Method 2: Using filter + first
        stmt = select(CompleteUser).where(CompleteUser.username == "alice")
        user = session.execute(stmt).scalar_one_or_none()

        if user:
            print(f"Found: {user.username}")


def select_by_primary_key():
    """Get record by ID (fastest method)"""

    with SessionLocal() as session:
        # session.get() is optimized for PK lookups
        user = session.get(CompleteUser, 1)  # Get user with id=1

        if user:
            print(f"User #1: {user.username}")

        # Equivalent using select (slower)
        stmt = select(CompleteUser).where(CompleteUser.id == 1)
        user2 = session.execute(stmt).scalar_one_or_none()


def select_with_filtering():
    """WHERE clauses — filtering results"""

    with SessionLocal() as session:
        # Simple equality
        stmt = select(CompleteUser).where(CompleteUser.is_active == True)
        active_users = session.execute(stmt).scalars().all()
        print(f"Active users: {len(active_users)}")

        # Not equal
        stmt = select(CompleteUser).where(CompleteUser.is_active != False)

        # Greater than / less than
        stmt = select(CompleteUser).where(CompleteUser.id > 5)

        # IN clause
        stmt = select(CompleteUser).where(
            CompleteUser.username.in_(["alice", "bob", "charlie"])
        )

        # LIKE / ILIKE (case-sensitive / case-insensitive)
        stmt = select(CompleteUser).where(CompleteUser.email.ilike("%@example.com"))

        # IS NULL / IS NOT NULL
        stmt = select(CompleteUser).where(CompleteUser.email != None)  # NOT NULL
        stmt = select(CompleteUser).where(CompleteUser.email.is_(None))  # IS NULL

        # BETWEEN
        from sqlalchemy import between

        stmt = select(CompleteUser).where(between(CompleteUser.id, 1, 10))

        # Execute one example
        result = (
            session.execute(select(CompleteUser).where(CompleteUser.is_active == True))
            .scalars()
            .all()
        )

        return result


def select_with_and_or():
    """Combining multiple conditions"""

    with SessionLocal() as session:
        # AND conditions (all must be true)
        # Method 1: Multiple where() calls
        stmt = (
            select(CompleteUser)
            .where(CompleteUser.is_active == True)
            .where(CompleteUser.email_verified == True)
        )

        # Method 2: Using and_()
        stmt = select(CompleteUser).where(
            and_(CompleteUser.is_active == True, CompleteUser.email_verified == True)
        )

        # OR conditions (any can be true)
        stmt = select(CompleteUser).where(
            or_(CompleteUser.username == "alice", CompleteUser.username == "bob")
        )

        # Complex combination
        stmt = select(CompleteUser).where(
            and_(
                CompleteUser.is_active == True,
                or_(CompleteUser.email_verified == True, CompleteUser.id < 5),
            )
        )

        # NOT condition
        stmt = select(CompleteUser).where(not_(CompleteUser.is_active == False))

        result = session.execute(stmt).scalars().all()
        return result


# ============================================================
# 3️⃣ SORTING & PAGINATION
# ============================================================


def sorting_results():
    """ORDER BY — sorting results"""

    with SessionLocal() as session:
        # Ascending order (default)
        stmt = select(CompleteUser).order_by(CompleteUser.username)

        # Descending order
        stmt = select(CompleteUser).order_by(desc(CompleteUser.created_at))

        # Multiple sort columns
        stmt = select(CompleteUser).order_by(
            desc(CompleteUser.is_active),  # Active users first
            asc(CompleteUser.username),  # Then alphabetically
        )

        # NULL handling
        stmt = select(CompleteUser).order_by(
            nullsfirst(CompleteUser.email)  # NULLs at beginning
        )
        stmt = select(CompleteUser).order_by(
            nullslast(CompleteUser.email)  # NULLs at end
        )

        result = session.execute(stmt).scalars().all()
        return result


def pagination():
    """LIMIT & OFFSET — pagination"""

    with SessionLocal() as session:
        page_size = 5
        page_number = 1  # First page

        # Calculate offset
        offset = (page_number - 1) * page_size

        # Get page 1 (items 1-5)
        stmt = select(CompleteUser).limit(page_size).offset(offset)
        page1 = session.execute(stmt).scalars().all()

        # Get page 2 (items 6-10)
        page_number = 2
        offset = (page_number - 1) * page_size
        stmt = select(CompleteUser).limit(page_size).offset(offset)
        page2 = session.execute(stmt).scalars().all()

        print(f"Page 1: {[u.username for u in page1]}")
        print(f"Page 2: {[u.username for u in page2]}")


def count_and_exists():
    """COUNT and EXISTS queries"""

    with SessionLocal() as session:
        # Count all users
        count_stmt = select(func.count(CompleteUser.id))
        total = session.execute(count_stmt).scalar()
        print(f"Total users: {total}")

        # Count with filter
        count_stmt = select(func.count(CompleteUser.id)).where(
            CompleteUser.is_active == True
        )
        active_count = session.execute(count_stmt).scalar()

        # Count distinct
        distinct_stmt = select(func.count(distinct(CompleteUser.email)))
        unique_emails = session.execute(distinct_stmt).scalar()

        # EXISTS check
        exists_stmt = select(exists().where(CompleteUser.username == "admin"))
        has_admin = session.execute(exists_stmt).scalar()
        print(f"Has admin user: {has_admin}")


# ============================================================
# 4️⃣ AGGREGATION & GROUPING
# ============================================================


def aggregation_examples():
    """SUM, AVG, MIN, MAX, COUNT with GROUP BY"""

    with SessionLocal() as session:
        # Create some sample book data if needed
        # Aggregate functions

        # Count books per author
        stmt = (
            select(Author.name, func.count(Book.id).label("book_count"))
            .join(Book, Author.books)
            .group_by(Author.id)
        )

        results = session.execute(stmt).all()
        for author_name, book_count in results:
            print(f"{author_name}: {book_count} books")

        # HAVING clause (filter groups)
        stmt = (
            select(Author.name, func.count(Book.id).label("book_count"))
            .join(Book)
            .group_by(Author.id)
            .having(func.count(Book.id) > 1)
        )

        # Multiple aggregations
        stmt = select(
            func.min(CompleteUser.id),
            func.max(CompleteUser.id),
            func.avg(CompleteUser.id),
        )
        min_id, max_id, avg_id = session.execute(stmt).one()


def grouping_with_case():
    """CASE statements in queries"""

    with SessionLocal() as session:
        # Categorize users
        stmt = select(
            CompleteUser.username,
            case(
                (CompleteUser.id < 5, "Early Adopter"),
                (CompleteUser.id < 10, "Regular"),
                else_="Late Joiner",
            ).label("user_category"),
        )

        results = session.execute(stmt).all()
        for username, category in results:
            print(f"{username}: {category}")


# ============================================================
# 5️⃣ JOINS
# ============================================================


def join_examples():
    """Different types of JOINs"""

    with SessionLocal() as session:
        # INNER JOIN (default) — only matching rows
        stmt = select(Author, Book).join(Book, Author.books)
        results = session.execute(stmt).all()
        # Returns list of (Author, Book) tuples

        # LEFT OUTER JOIN — all authors, books if they exist
        stmt = select(Author, Book).outerjoin(Book, Author.books)

        # Join with filter
        stmt = select(Author).join(Book).where(Book.title.ilike("%potter%"))

        # Join specific columns
        stmt = select(Author.name, Book.title).join(Book)
        results = session.execute(stmt).all()

        # Self-join (e.g., employees and managers)
        Manager = aliased(Employee)
        stmt = select(Employee.name, Manager.name.label("manager_name")).outerjoin(
            Manager, Employee.manager_id == Manager.id
        )


# ============================================================
# 6️⃣ UPDATE OPERATIONS
# ============================================================


def update_single_record():
    """Update one record"""

    with SessionLocal() as session:
        # Get the record
        user = session.get(CompleteUser, 1)

        if user:
            # Modify (not in DB yet)
            user.email = "newemail@example.com"
            user.is_active = False

            # Commit changes
            session.commit()
            print(f"Updated user: {user.username}")


def update_multiple_records():
    """Update multiple records at once"""

    with SessionLocal() as session:
        # Update all inactive users
        stmt = (
            update(CompleteUser)
            .where(CompleteUser.is_active == False)
            .values(email_verified=False)
        )

        result = session.execute(stmt)
        session.commit()

        print(f"Updated {result.rowcount} rows")


def update_with_returning():
    """Update and return updated values"""

    with SessionLocal() as session:
        stmt = (
            update(CompleteUser)
            .where(CompleteUser.id == 1)
            .values(is_active=True)
            .returning(CompleteUser.id, CompleteUser.username)
        )

        result = session.execute(stmt)
        updated = result.fetchone()
        session.commit()

        if updated:
            print(f"Updated: ID={updated.id}, Username={updated.username}")


# ============================================================
# 7️⃣ DELETE OPERATIONS
# ============================================================


def delete_single_record():
    """Delete one record"""

    with SessionLocal() as session:
        # Get and delete
        user = session.get(CompleteUser, 999)  # Non-existent ID

        if user:
            session.delete(user)
            session.commit()
            print(f"Deleted user: {user.username}")
        else:
            print("User not found")


def delete_with_cascade():
    """Delete parent cascades to children"""

    with SessionLocal() as session:
        author = session.get(Author, 1)

        if author:
            book_count = len(author.books)
            session.delete(author)
            session.commit()
            print(f"Deleted author and {book_count} books")


def bulk_delete():
    """Delete multiple records at once"""

    with SessionLocal() as session:
        # Delete inactive users created more than 1 year ago
        one_year_ago = datetime.utcnow() - timedelta(days=365)

        stmt = (
            delete(CompleteUser)
            .where(CompleteUser.is_active == False)
            .where(CompleteUser.created_at < one_year_ago)
        )

        result = session.execute(stmt)
        session.commit()

        print(f"Deleted {result.rowcount} old inactive users")


# ============================================================
# 8️⃣ TRANSACTIONS — THE MOST IMPORTANT TOPIC
# ============================================================
"""
Transactions ensure data consistency. All operations in a transaction
succeed together or fail together (rollback).

ACID Properties:
• Atomicity: All or nothing
• Consistency: Database remains valid
• Isolation: Transactions don't interfere
• Durability: Committed data survives crashes
"""


def basic_transaction():
    """Understanding commit and rollback"""

    with SessionLocal() as session:
        try:
            # Start implicit transaction

            user1 = CompleteUser(
                username="tx_user1", email="tx1@test.com", password="pass123"
            )
            user2 = CompleteUser(
                username="tx_user2", email="tx2@test.com", password="pass456"
            )

            session.add_all([user1, user2])

            # SQL hasn't been sent yet (lazy)

            # Commit = Save to database
            session.commit()
            print("Transaction committed!")

        except Exception as e:
            # Rollback = Undo all changes
            session.rollback()
            print(f"Transaction rolled back: {e}")
            raise


def explicit_transaction_block():
    """Using session.begin() for cleaner transactions"""

    with SessionLocal() as session:
        with session.begin():
            # Everything in this block is one transaction
            user = CompleteUser(
                username="explicit_tx", email="explicit@test.com", password="pass123"
            )
            session.add(user)

            # Automatically committed at end of block
            # Automatically rolled back on exception

        print("Transaction completed!")


def transaction_with_rollback_demo():
    """Demonstrate rollback behavior"""

    with SessionLocal() as session:
        # Get initial count
        initial_count = session.execute(select(func.count(CompleteUser.id))).scalar()

        try:
            # Add a user
            user = CompleteUser(
                username="rollback_test", email="rollback@test.com", password="pass123"
            )
            session.add(user)

            # Verify added in session
            pending_count = session.execute(
                select(func.count(CompleteUser.id))
            ).scalar()
            print(f"Count in session (before commit): {pending_count}")

            # Force an error
            raise ValueError("Simulated error!")

            session.commit()  # Never reached

        except:
            session.rollback()
            print("Rolled back due to error")

        # Verify database unchanged
        final_count = session.execute(select(func.count(CompleteUser.id))).scalar()
        print(f"Initial: {initial_count}, Final: {final_count}")
        print(f"Match: {initial_count == final_count}")


def savepoints():
    """Nested transactions with savepoints"""

    with SessionLocal() as session:
        with session.begin():
            # Outer transaction
            user1 = CompleteUser(
                username="outer_user", email="outer@test.com", password="pass123"
            )
            session.add(user1)

            # Create savepoint
            nested = session.begin_nested()

            try:
                # Inner transaction (savepoint)
                user2 = CompleteUser(
                    username="inner_user", email="inner@test.com", password="pass456"
                )
                session.add(user2)

                # Simulate error in nested transaction
                raise ValueError("Inner error!")

            except:
                nested.rollback()  # Rollback savepoint only
                print("Inner transaction rolled back")

            # Outer transaction continues
            # user1 still exists, user2 was rolled back
            print("Outer transaction continues...")

        print("Outer transaction committed!")


def handling_integrity_errors():
    """Handling unique constraint violations"""

    with SessionLocal() as session:
        try:
            with session.begin():
                # Try to insert duplicate username
                user = CompleteUser(
                    username="alice",  # Already exists!
                    email="unique@test.com",
                    password="pass123",
                )
                session.add(user)
                # Will raise IntegrityError on commit

        except IntegrityError as e:
            print(f"Integrity error: {e}")
            # Already rolled back by session.begin()

            # Can now create new transaction
            user = CompleteUser(
                username="alice_unique_123", email="unique@test.com", password="pass123"
            )
            session.add(user)
            session.commit()
            print("Created user with unique username")


# ============================================================
# 9️⃣ COMMON PATTERNS & BEST PRACTICES
# ============================================================


def get_or_create():
    """Pattern: Get existing or create new"""

    with SessionLocal() as session:
        username = "new_or_existing"
        email = "getorcreate@test.com"

        # Try to get existing
        stmt = select(CompleteUser).where(CompleteUser.username == username)
        user = session.execute(stmt).scalar_one_or_none()

        if user is None:
            # Create new
            user = CompleteUser(username=username, email=email, password="defaultpass")
            session.add(user)
            session.commit()
            print(f"Created new user: {username}")
        else:
            print(f"Found existing user: {username}")

        return user


def bulk_operations_efficient():
    """Efficient bulk operations"""

    with SessionLocal() as session:
        # Bulk insert (most efficient)
        session.execute(
            insert(CompleteUser),
            [
                {
                    "username": f"bulk_{i}",
                    "email": f"bulk_{i}@test.com",
                    "password_hash": f"hash{i}",
                }
                for i in range(1000, 1010)
            ],
        )
        session.commit()

        # Bulk update
        session.execute(
            update(CompleteUser),
            [{"id": 1, "is_active": False}, {"id": 2, "is_active": False}],
        )
        session.commit()


def query_with_eager_loading():
    """Avoid N+1 problem with eager loading"""

    with SessionLocal() as session:
        # BAD: N+1 problem
        print("\n--- BAD (N+1 queries) ---")
        authors = session.execute(select(Author)).scalars().all()
        for author in authors[:3]:  # 1 query for authors
            for book in author.books:  # + N queries for books!
                print(f"{author.name}: {book.title}")

        # GOOD: Eager loading
        print("\n--- GOOD (2 queries total) ---")
        authors = (
            session.execute(select(Author).options(selectinload(Author.books)))
            .scalars()
            .all()
        )

        for author in authors[:3]:
            for book in author.books:  # No additional queries!
                print(f"{author.name}: {book.title}")


def session_scopes():
    """Understanding session lifecycle"""

    # Method 1: Context manager (recommended)
    with SessionLocal() as session:
        user = session.get(CompleteUser, 1)
        # Session auto-closed at end of block

    # Method 2: Manual management
    session = SessionLocal()
    try:
        user = session.get(CompleteUser, 1)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    # Method 3: Generator for dependency injection
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


# ============================================================
# 10️⃣ COMMON PITFALLS & SOLUTIONS
# ============================================================
"""
PITFALL 1: Modifying detached objects
-------------------------------------
# WRONG
user = session.get(User, 1)
session.close()
user.name = "New Name"  # ERROR: DetachedInstanceError

# RIGHT
with SessionLocal() as session:
    user = session.get(User, 1)
    user.name = "New Name"
    session.commit()


PITFALL 2: Forgetting to commit
-------------------------------
# WRONG
session.add(user)
# User never saved!

# RIGHT
session.add(user)
session.commit()


PITFALL 3: Lazy loading after session closes
--------------------------------------------
# WRONG
with SessionLocal() as session:
    user = session.get(User, 1)
# Session closed
print(user.posts)  # ERROR: Can't lazy load

# RIGHT
with SessionLocal() as session:
    user = session.get(User, 1)
    print(user.posts)  # Load while session active


PITFALL 4: Not handling exceptions
----------------------------------
# WRONG
try:
    session.add(user)
    session.commit()
except:
    pass  # Session in bad state!

# RIGHT
try:
    with session.begin():
        session.add(user)
except:
    # Automatically rolled back
    pass


PITFALL 5: Loading too much data
--------------------------------
# WRONG (loads all columns)
users = session.execute(select(User)).scalars().all()

# RIGHT (only needed columns)
stmt = select(User.id, User.username)
results = session.execute(stmt).all()


PITFALL 6: Not using indexes for filters
-----------------------------------------
# SLOW (table scan)
SELECT * FROM users WHERE email = 'x'
# Without index on email column

# FAST (index scan)
# With index on email column
"""


# ============================================================
# 11️⃣ QUICK REFERENCE CHEAT SHEET
# ============================================================
"""
QUICK REFERENCE
===============

CREATE:
-------
# Single record
user = User(name="John")
session.add(user)
session.commit()

# Multiple records
session.add_all([user1, user2, user3])
session.commit()

# Bulk insert
session.execute(insert(User), [{"name": "A"}, {"name": "B"}])
session.commit()


READ:
-----
# By ID
user = session.get(User, 1)

# All records
users = session.execute(select(User)).scalars().all()

# First matching
user = session.execute(select(User).where(User.name == "John")).scalar_one_or_none()

# With filter
stmt = select(User).where(User.active == True)

# With multiple conditions
stmt = select(User).where(and_(User.active == True, User.age > 18))

# With OR
stmt = select(User).where(or_(User.role == "admin", User.role == "moderator"))

# With sorting
stmt = select(User).order_by(desc(User.created_at))

# With pagination
stmt = select(User).limit(10).offset(20)

# Count
count = session.execute(select(func.count(User.id))).scalar()

# Exists
has_users = session.execute(select(exists().where(User.active == True))).scalar()


UPDATE:
-------
# Single record
user = session.get(User, 1)
user.name = "New Name"
session.commit()

# Multiple records
session.execute(update(User).where(User.active == False).values(active=True))
session.commit()

# With returning
result = session.execute(
    update(User).where(User.id == 1).values(name="X").returning(User.id)
)
session.commit()


DELETE:
-------
# Single record
user = session.get(User, 1)
session.delete(user)
session.commit()

# Multiple records
session.execute(delete(User).where(User.active == False))
session.commit()


TRANSACTIONS:
-------------
# Basic
try:
    session.add(user)
    session.commit()
except:
    session.rollback()
    raise

# With context manager
with session.begin():
    session.add(user)
    # Auto commit/rollback

# With savepoint
with session.begin():
    session.add(user1)
    with session.begin_nested():
        session.add(user2)
        # Can rollback just this part


EAGER LOADING:
--------------
from sqlalchemy.orm import selectinload, joinedload

# Load relationships efficiently
users = session.execute(
    select(User).options(selectinload(User.posts))
).scalars().all()


AGGREGATION:
------------
from sqlalchemy import func

# Count
select(func.count(User.id))

# Sum
select(func.sum(Order.amount))

# Group by
select(User.role, func.count(User.id)).group_by(User.role)

# Having
select(User.role, func.count(User.id)).group_by(User.role).having(func.count(User.id) > 5)


FILTERS:
--------
# Equality
.where(User.name == "John")

# Not equal
.where(User.name != "John")

# IN
.where(User.role.in_(["admin", "moderator"]))

# LIKE
.where(User.email.like("%@gmail.com"))
.where(User.email.ilike("%@GMAIL.COM"))  # Case-insensitive

# NULL check
.where(User.deleted_at.is_(None))
.where(User.deleted_at.is_not(None))

# BETWEEN
.where(User.age.between(18, 65))
"""


if __name__ == "__main__":
    print("=" * 60)
    print("SQLALCHEMY ORM QUERYING TUTORIAL")
    print("=" * 60)
    print("\nThis file contains comprehensive examples.")
    print("Import and call functions to see them in action:")
    print("\n  from orm_querying_tutorial import *")
    print("  create_single_record()")
    print("  select_all_records()")
    print("  basic_transaction()")
    print("\nMake sure your database is set up first!")
