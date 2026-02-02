"""
SQLALCHEMY ORM RELATIONSHIPS — COMPLETE GUIDE FOR BEGINNERS
===========================================================

This file covers everything you need to understand about ORM relationships:
• One-to-Many (Parent → Children)
• Many-to-One (Child → Parent)
• One-to-One
• Many-to-Many
• Foreign Keys
• Back References (back_populates)
• Lazy vs Eager Loading
• Cascades
• Joins
• Association Tables
"""

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    ForeignKey,
    Table,
    Column,
    DateTime,
    Text,
    Boolean,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
    sessionmaker,
)
from datetime import datetime
from typing import List, Optional
import uuid

# ============================================================
# DATABASE SETUP
# ============================================================

engine = create_engine(
    "postgresql+psycopg2://postgres:1729@localhost:5432/newdb", echo=True
)


class Base(DeclarativeBase):
    pass


# ============================================================
# 1️⃣ ONE-TO-MANY RELATIONSHIP
# ============================================================
"""
ONE-TO-MANY = One parent has many children

Example: One Author writes many Books
         Author (1) ───────► Book (N)

In Database Terms:
• The "many" side (Book) has the foreign key
• The "one" side (Author) doesn't store anything in its table
"""


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # This creates the relationship in Python (NOT in database!)
    # List[Book] tells SQLAlchemy: "One author has MANY books"
    books: Mapped[List["Book"]] = relationship(
        back_populates="author",  # Links to Book.author
        cascade="all, delete-orphan",  # When author deleted, delete their books
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    # This is the ACTUAL foreign key in the database
    # It stores which author wrote this book
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    # This creates the reverse relationship
    # "Many books belong to ONE author"
    author: Mapped["Author"] = relationship(back_populates="books")


"""
VISUAL REPRESENTATION:

Database Tables:
┌─────────────────┐         ┌─────────────────┐
│     authors     │         │      books      │
├─────────────────┤         ├─────────────────┤
│ id (PK) │ name  │         │ id(PK)│ title   │
├─────────┼───────┤         ├───────┼─────────┤
│    1    │ Alice │         │   1   │ Book A  │
│    2    │  Bob  │         │   2   │ Book B  │ ← author_id = 1 (Alice)
└─────────┴───────┘         │   3   │ Book C  │ ← author_id = 2 (Bob)
                            └───────┴─────────┘

In Python (ORM Objects):

author_alice = Author(name="Alice")
author_alice.books = [Book(title="Book A"), Book(title="Book B")]

# Access from parent to children:
for book in author_alice.books:
    print(book.title)  # "Book A", "Book B"

# Access from child to parent:
book_a = author_alice.books[0]
print(book_a.author.name)  # "Alice"
"""


# ============================================================
# 2️⃣ MANY-TO-ONE RELATIONSHIP (Same as One-to-Many, reversed)
# ============================================================
"""
MANY-TO-ONE = Many children point to one parent

This is the SAME relationship as One-to-Many, just viewed from
the child's perspective.

Example: Many Employees work in one Department
         Employee (N) ───────► Department (1)
"""


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # One department has many employees
    employees: Mapped[List["Employee"]] = relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # Foreign key: which department?
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))

    # Many employees belong to one department
    department: Mapped["Department"] = relationship(back_populates="employees")


"""
VISUAL:
dept = Department(name="Engineering")
emp1 = Employee(name="John", department=dept)
emp2 = Employee(name="Jane", department=dept)

# Access:
dept.employees  # [emp1, emp2]
emp1.department  # dept
emp1.department.name  # "Engineering"
"""


# ============================================================
# 3️⃣ ONE-TO-ONE RELATIONSHIP
# ============================================================
"""
ONE-TO-ONE = One parent has exactly one child, and vice versa

Example: One User has exactly one Profile
         User (1) ───────► Profile (1)

Implementation:
• Same as One-to-Many, but we add `uselist=False`
• This tells SQLAlchemy: "Only ONE item, not a list"
"""


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # One user has ONE profile (not a list!)
    profile: Mapped[Optional["Profile"]] = relationship(
        back_populates="user",
        uselist=False,  # ← This makes it one-to-one
        cascade="all, delete-orphan",
    )


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign key with UNIQUE constraint (ensures one-to-one)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,  # ← This enforces one-to-one in database
    )

    # One profile belongs to ONE user
    user: Mapped["User"] = relationship(back_populates="profile")


"""
VISUAL:
user = User(username="alice")
user.profile = Profile(bio="I love coding!")

# Access:
user.profile.bio  # "I love coding!"
user.profile.user.username  # "alice" (back reference)

WITHOUT uselist=False, user.profile would be a list [profile]
WITH uselist=False, user.profile is a single object profile
"""


# ============================================================
# 4️⃣ MANY-TO-MANY RELATIONSHIP
# ============================================================
"""
MANY-TO-MANY = Multiple parents can have multiple children

Example: Students take many Courses, Courses have many Students
         Student (N) ◄──────► Course (N)

Implementation:
• We need a THIRD table called "Association Table" or "Join Table"
• This table only has foreign keys, linking the two main tables
"""

# Association Table (the "link" between students and courses)
student_course_association = Table(
    "student_courses",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # Many-to-many relationship
    # secondary= tells SQLAlchemy which table to use for the link
    courses: Mapped[List["Course"]] = relationship(
        secondary=student_course_association, back_populates="students"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    # Reverse side
    students: Mapped[List["Student"]] = relationship(
        secondary=student_course_association, back_populates="courses"
    )


"""
VISUAL REPRESENTATION:

Main Tables:                    Association Table (student_courses):
┌─────────────────┐            ┌─────────────────────────┐
│    students     │            │ student_id │ course_id  │
├─────────────────┤            ├────────────┼────────────┤
│ id (PK) │ name  │            │     1      │     1      │ ← Alice takes Math
│    1    │ Alice │            │     1      │     2      │ ← Alice takes Physics
│    2    │  Bob  │            │     2      │     1      │ ← Bob takes Math
└─────────┴───────┘            │     2      │     3      │ ← Bob takes Chemistry
                               └────────────┴────────────┘
┌─────────────────┐
│     courses     │
├─────────────────┤
│ id (PK) │ title │
├─────────┼───────┤
│    1    │ Math  │
│    2    │Physics│
│    3    │Chem   │
└─────────┴───────┘

In Python:
alice = Student(name="Alice")
bob = Student(name="Bob")

math = Course(title="Mathematics")
physics = Course(title="Physics")
chem = Course(title="Chemistry")

# Enroll students in courses
alice.courses = [math, physics]  # Alice takes 2 courses
bob.courses = [math, chem]       # Bob takes 2 courses

# Check who takes math:
math.students  # [alice, bob]

# Check what Alice takes:
alice.courses  # [math, physics]
"""


# ============================================================
# 5️⃣ BACK_POPULATES — THE MAGIC OF TWO-WAY ACCESS
# ============================================================
"""
back_populates = Connects two sides of a relationship

Without it:
  author.books  # Works ✓
  book.author   # ERROR! Doesn't know about the reverse

With it:
  author.books  # Works ✓
  book.author   # Works ✓ (automatically connected!)

When you set: author.books = [book1, book2]
SQLAlchemy automatically sets: book1.author = author, book2.author = author
"""


# ============================================================
# 6️⃣ LAZY vs EAGER LOADING
# ============================================================
"""
LAZY LOADING (default):
• Related data is loaded ONLY when you access it
• Pros: Fast initial query, saves memory if you don't need related data
• Cons: N+1 query problem (many small queries)

EAGER LOADING:
• Related data is loaded in the SAME query
• Pros: Fewer queries, better performance
• Cons: Slower initial query, more memory

Types of Eager Loading:
• joinedload() - Uses SQL JOIN (one big query)
• selectinload() - Uses IN clause (two queries, very efficient)
• subqueryload() - Uses subquery (less common now)
"""

from sqlalchemy.orm import joinedload, selectinload

"""
EXAMPLES:

# LAZY (default) - Triggers extra queries when accessing .books
authors = session.execute(select(Author)).scalars().all()
for author in authors:
    print(author.name)
    for book in author.books:  # ← NEW QUERY for each author!
        print(f"  - {book.title}")
        
# If you have 100 authors, this makes 101 queries! (1 + 100)


# EAGER with joinedload() - Everything in ONE query
authors = session.execute(
    select(Author).options(joinedload(Author.books))
).scalars().unique().all()

for author in authors:
    print(author.name)
    for book in author.books:  # ← No new query, already loaded!
        print(f"  - {book.title}")


# EAGER with selectinload() - Two queries, but very efficient
authors = session.execute(
    select(Author).options(selectinload(Author.books))
).scalars().all()

# First query: SELECT * FROM authors
# Second query: SELECT * FROM books WHERE author_id IN (1, 2, 3, ...)
"""


# ============================================================
# 7️⃣ CASCADES — AUTOMATIC ACTIONS
# ============================================================
"""
Cascades tell SQLAlchemy what to do automatically

Common cascade options:
• "all" = shorthand for all operations
• "delete" = when parent deleted, delete children
• "delete-orphan" = when child removed from parent, delete it
• "save-update" = when parent saved, save children too
• "merge" = when parent merged, merge children
• "refresh-expire" = when parent refreshed, refresh children
• "expunge" = when parent removed from session, remove children

Most common combo: cascade="all, delete-orphan"
"""

"""
EXAMPLE:

class Author(Base):
    books: Mapped[List["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"  # ← Magic happens here
    )

# What this does:

# 1. Save cascade:
author = Author(name="Alice")
author.books = [Book(title="Book 1"), Book(title="Book 2")]
session.add(author)
session.commit()  # Both author AND books saved automatically!

# 2. Delete cascade:
session.delete(author)
session.commit()  # Author AND all their books deleted!

# 3. Orphan delete:
author.books.remove(book1)  # Remove from relationship
session.commit()  # book1 is automatically deleted from database!

# Without delete-orphan:
# book1 would still exist in DB with author_id=NULL (orphaned)
"""


# ============================================================
# 8️⃣ JOINS — QUERYING ACROSS TABLES
# ============================================================
"""
JOIN combines rows from two or more tables based on a related column

Types:
• INNER JOIN (default) - Only matching rows from both tables
• LEFT OUTER JOIN - All rows from left table, matching from right
• RIGHT OUTER JOIN - All rows from right table, matching from left
• FULL OUTER JOIN - All rows from both tables
"""

from sqlalchemy import join, outerjoin

"""
EXAMPLES:

# INNER JOIN: Get authors who have books
stmt = select(Author).join(Author.books)
# SQL: SELECT * FROM authors JOIN books ON authors.id = books.author_id


# LEFT OUTER JOIN: Get all authors, with books if they have any
stmt = select(Author).outerjoin(Author.books)
# SQL: SELECT * FROM authors LEFT OUTER JOIN books ...


# JOIN with filter: Find authors who wrote "Python Guide"
stmt = select(Author).join(Author.books).where(Book.title == "Python Guide")


# Get specific columns from both tables
stmt = select(Author.name, Book.title).join(Author.books)
result = session.execute(stmt)
for author_name, book_title in result:
    print(f"{author_name} wrote {book_title}")


# Complex query with multiple joins
stmt = (
    select(Student, Course, Department)
    .join(Student.courses)
    .join(Course.department)
    .where(Department.name == "Engineering")
)
"""


# ============================================================
# 9️⃣ COMPLETE WORKING EXAMPLE
# ============================================================


def demonstrate_relationships():
    """Complete working example of all relationship types"""

    # Create tables
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        print("\n" + "=" * 60)
        print("CREATING DATA")
        print("=" * 60)

        # One-to-Many: Author -> Books
        author_alice = Author(name="Alice")
        author_alice.books = [
            Book(title="Python Basics"),
            Book(title="Advanced Python"),
        ]

        author_bob = Author(name="Bob")
        author_bob.books = [Book(title="Java Guide")]

        session.add_all([author_alice, author_bob])

        # Many-to-One: Employee -> Department
        eng_dept = Department(name="Engineering")
        hr_dept = Department(name="HR")

        emp_john = Employee(name="John", department=eng_dept)
        emp_jane = Employee(name="Jane", department=eng_dept)
        emp_mike = Employee(name="Mike", department=hr_dept)

        session.add_all([eng_dept, hr_dept])

        # One-to-One: User -> Profile
        user_charlie = User(username="charlie")
        user_charlie.profile = Profile(bio="Software Developer")

        session.add(user_charlie)

        # Many-to-Many: Students <-> Courses
        student_dave = Student(name="Dave")
        student_eve = Student(name="Eve")

        course_math = Course(title="Mathematics")
        course_physics = Course(title="Physics")
        course_chem = Course(title="Chemistry")

        student_dave.courses = [course_math, course_physics]
        student_eve.courses = [course_math, course_chem]

        session.add_all([student_dave, student_eve])

        session.commit()

        print("\n" + "=" * 60)
        print("QUERYING DATA")
        print("=" * 60)

        # Query with eager loading
        print("\n--- Authors and their books (eager loaded) ---")
        authors = (
            session.execute(select(Author).options(selectinload(Author.books)))
            .scalars()
            .all()
        )

        for author in authors:
            print(f"\n{author.name} wrote:")
            for book in author.books:
                print(f"  - {book.title}")

        # Query many-to-one
        print("\n--- Employees and their departments ---")
        employees = session.execute(select(Employee)).scalars().all()
        for emp in employees:
            print(f"{emp.name} works in {emp.department.name}")

        # Query one-to-one
        print("\n--- User profile ---")
        user = session.execute(select(User)).scalar_one()
        print(f"{user.username}'s bio: {user.profile.bio}")

        # Query many-to-many
        print("\n--- Students and courses ---")
        students = (
            session.execute(select(Student).options(selectinload(Student.courses)))
            .scalars()
            .all()
        )

        for student in students:
            print(f"\n{student.name} is enrolled in:")
            for course in student.courses:
                print(f"  - {course.title}")

        # Reverse: courses with students
        print("\n--- Courses and enrolled students ---")
        courses = (
            session.execute(select(Course).options(selectinload(Course.students)))
            .scalars()
            .all()
        )

        for course in courses:
            student_names = [s.name for s in course.students]
            print(f"{course.title}: {', '.join(student_names)}")

        # Demonstrate cascade delete
        print("\n" + "=" * 60)
        print("CASCADE DELETE DEMONSTRATION")
        print("=" * 60)

        print(f"\nBefore delete: {len(author_alice.books)} books by Alice")
        session.delete(author_alice)
        session.commit()

        # Verify books are deleted too
        remaining_books = session.execute(select(Book)).scalars().all()
        print(f"After deleting Alice: {len(remaining_books)} books remain")
        for book in remaining_books:
            print(f"  - {book.title} by {book.author.name}")


if __name__ == "__main__":
    demonstrate_relationships()


# ============================================================
# 🔟 QUICK REFERENCE CHEAT SHEET
# ============================================================
"""
QUICK REFERENCE
===============

ONE-TO-MANY:
------------
class Parent(Base):
    children: Mapped[List["Child"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan"
    )

class Child(Base):
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id"))
    parent: Mapped["Parent"] = relationship(back_populates="children")


MANY-TO-ONE:
------------
(Same as above, just view from Child side)


ONE-TO-ONE:
-----------
class User(Base):
    profile: Mapped[Optional["Profile"]] = relationship(
        back_populates="user",
        uselist=False
    )

class Profile(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True
    )
    user: Mapped["User"] = relationship(back_populates="profile")


MANY-TO-MANY:
-------------
association_table = Table(
    "association",
    Base.metadata,
    Column("left_id", ForeignKey("left.id"), primary_key=True),
    Column("right_id", ForeignKey("right.id"), primary_key=True)
)

class Left(Base):
    rights: Mapped[List["Right"]] = relationship(
        secondary=association_table,
        back_populates="lefts"
    )

class Right(Base):
    lefts: Mapped[List["Left"]] = relationship(
        secondary=association_table,
        back_populates="rights"
    )


EAGER LOADING:
--------------
from sqlalchemy.orm import joinedload, selectinload

# Use joinedload for one-to-many (single query)
select(Parent).options(joinedload(Parent.children))

# Use selectinload for many-to-many or large datasets (two queries, efficient)
select(Parent).options(selectinload(Parent.children))


JOINS:
------
from sqlalchemy import join

# Inner join
select(Parent).join(Parent.children)

# Outer join  
select(Parent).outerjoin(Parent.children)

# Join with filter
select(Parent).join(Parent.children).where(Child.name == "x")


CASCADES:
---------
"all" - all operations
"delete" - delete children with parent
"delete-orphan" - delete child when removed from parent
"save-update" - save children with parent
"merge" - merge children with parent

Most common: cascade="all, delete-orphan"
"""
