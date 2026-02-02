"""
SQLALCHEMY ORM MODELS — COMPLETE MASTERY GUIDE
==============================================

This file covers EVERYTHING you need to know about creating ORM models:
• DeclarativeBase and model structure
• Column types and constraints
• Primary/Foreign keys
• Default values and auto-generation
• Validation and computed properties
• Indexes and performance
• Table configuration
• Mixins for reusable code
• Inheritance strategies
• What goes to DB vs Python-only
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Annotated
import uuid
import enum

from sqlalchemy import (
    create_engine, String, Integer, Boolean, DateTime, Date, 
    Numeric, Float, Text, LargeBinary, JSON, Enum, UUID,
    ForeignKey, UniqueConstraint, CheckConstraint, Index,
    Column, Table, text, event, func
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
    validates, column_property, synonym, declared_attr
)
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import expression


# ============================================================
# 1️⃣ THE FOUNDATION — DECLARATIVE BASE
# ============================================================
"""
DeclarativeBase is the foundation of SQLAlchemy ORM models.
Think of it as the "base class" that gives your models ORM superpowers.

WHAT IT DOES (Python-side):
• Tracks all your model classes
• Generates table names automatically (if not specified)
• Provides metadata for creating/dropping tables
• Enables relationship definitions

WHAT REACHES THE DATABASE:
• NOTHING from DeclarativeBase itself reaches the database
• It's purely a Python construct for ORM management
"""

class Base(DeclarativeBase):
    """
    All your models inherit from this class.
    You can add common functionality here that all models share.
    """
    pass


# ============================================================
# 2️⃣ BASIC MODEL STRUCTURE
# ============================================================
"""
MODEL = Python Class ↔ Database Table

Class attributes = Columns in the table
Instances of class = Rows in the table
"""

class User(Base):
    """
    Simplest possible model.
    
    WHAT REACHES DATABASE:
    • Table name: "users"
    • Columns: id, username, email
    • Primary key constraint on 'id'
    
    WHAT STAYS IN PYTHON:
    • The class itself (User)
    • The __tablename__ attribute value
    • Docstrings and comments
    """
    
    __tablename__ = "users"  # ← This STRING reaches DB as table name
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))


# ============================================================
# 3️⃣ COLUMN TYPES — PYTHON ↔ DATABASE MAPPING
# ============================================================
"""
SQLAlchemy maps Python types to database types.

Python Type        SQLAlchemy Type        Database Type (PostgreSQL)
─────────────────────────────────────────────────────────────────────
int                Integer                INTEGER
str                String(100)            VARCHAR(100)
str                Text                   TEXT
float              Float                  REAL
float              Numeric(10,2)          NUMERIC(10,2)
bool               Boolean                BOOLEAN
datetime           DateTime               TIMESTAMP
date               Date                   DATE
bytes              LargeBinary            BYTEA
dict/list          JSON                   JSON
uuid.UUID          UUID                   UUID
Enum class         Enum(EnumClass)        ENUM or VARCHAR

WHAT REACHES DATABASE:
• The SQLAlchemy type determines the database column type
• Constraints (nullable, default, etc.)

WHAT STAYS IN PYTHON:
• The Python type hint (Mapped[int])
• It's used for IDE support and type checking, NOT for DB
"""

class DataTypesExample(Base):
    """Model showing all common data types"""
    
    __tablename__ = "data_types_example"
    
    # Integer types
    id: Mapped[int] = mapped_column(primary_key=True)
    small_num: Mapped[int] = mapped_column(Integer)  # Regular int
    big_num: Mapped[int] = mapped_column(Integer)    # Same in PG
    
    # String types
    short_text: Mapped[str] = mapped_column(String(50))   # VARCHAR(50)
    long_text: Mapped[str] = mapped_column(Text)          # TEXT (unlimited)
    
    # Numeric types
    regular_float: Mapped[float] = mapped_column(Float)               # REAL
    precise_decimal: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # DECIMAL(10,2)
    
    # Boolean
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Date/Time
    created_at: Mapped[datetime] = mapped_column(DateTime)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Binary data
    file_content: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    
    # JSON (flexible data)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # UUID
    uuid_field: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4  # Python generates UUID
    )


# ============================================================
# 4️⃣ COLUMN CONSTRAINTS
# ============================================================
"""
Constraints enforce rules on your data.

WHAT REACHES DATABASE:
• PRIMARY KEY - Unique identifier for row
• FOREIGN KEY - Links to another table
• UNIQUE - No duplicate values allowed
• NOT NULL - Column must have value (nullable=False)
• CHECK - Custom validation rule
• DEFAULT - Auto-fill value if not provided

WHAT STAYS IN PYTHON:
• Validation methods (@validates decorator)
• Hybrid properties (computed columns)
"""

class ConstraintsExample(Base):
    """Model showing all constraint types"""
    
    __tablename__ = "constraints_example"
    
    # PRIMARY KEY
    # Database: Creates unique index, NOT NULL constraint
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # NOT NULL (nullable=False)
    # Database: Column cannot be NULL
    required_field: Mapped[str] = mapped_column(
        String(100),
        nullable=False  # ← Reaches DB as NOT NULL constraint
    )
    
    # NULLABLE (nullable=True, default)
    # Database: Column CAN be NULL
    optional_field: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True  # ← Reaches DB as NULLable column
    )
    
    # UNIQUE
    # Database: Creates unique index, prevents duplicates
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,  # ← Reaches DB as UNIQUE constraint
        nullable=False
    )
    
    # DEFAULT values
    # Can be set in Python OR database
    
    # Python-side default (ORM generates value)
    python_default: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow  # ← Python function, called by ORM
    )
    
    # Database-side default (DB generates value)
    db_default: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("NOW()")  # ← SQL expression, executed by DB
    )
    
    # CHECK constraint
    # Database: Validates condition on every insert/update
    age: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("age >= 0 AND age <= 150", name="check_age_range")
        # ↑ Reaches DB as CHECK constraint
    )
    
    # Auto-increment (SERIAL in PostgreSQL)
    # Database: Auto-generates sequential numbers
    sequence_num: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        unique=True
    )


# ============================================================
# 5️⃣ FOREIGN KEYS — LINKING TABLES
# ============================================================
"""
Foreign keys create relationships between tables.

WHAT REACHES DATABASE:
• ForeignKey("table.column") - Creates FK constraint in DB
• ondelete="CASCADE" - DB deletes child when parent deleted
• onupdate="CASCADE" - DB updates FK when PK changes

WHAT STAYS IN PYTHON:
• relationship() - ORM construct for object navigation
• back_populates - Python-side connection between objects
"""

class DepartmentFK(Base):
    """Parent table for FK example"""
    __tablename__ = "departments_fk"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class EmployeeFK(Base):
    """Child table with foreign key"""
    __tablename__ = "employees_fk"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # Basic foreign key
    # Database: FK constraint referencing departments_fk.id
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments_fk.id")
    )
    
    # Foreign key with CASCADE delete
    # Database: When department deleted, employees auto-deleted
    dept_cascade_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "departments_fk.id",
            ondelete="CASCADE",   # ← DB handles deletion
            onupdate="CASCADE"    # ← DB handles PK updates
        ),
        nullable=True
    )
    
    # Foreign key with SET NULL
    # Database: When department deleted, set this to NULL
    dept_nullable_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "departments_fk.id",
            ondelete="SET NULL"   # ← Sets NULL instead of deleting
        ),
        nullable=True
    )
    
    # Composite foreign key (multiple columns)
    # You'd use ForeignKeyConstraint for this in __table_args__


# ============================================================
# 6️⃣ PYTHON-SIDE VALIDATION
# ============================================================
"""
@validates decorator = Python validation before data hits DB

WHAT STAYS IN PYTHON:
• @validates methods - Run in Python before INSERT/UPDATE
• Can raise ValueError to prevent bad data
• Can transform/normalize data

WHAT REACHES DATABASE:
• The validated/transformed value
"""

class ValidatedUser(Base):
    """Model with Python-side validation"""
    
    __tablename__ = "validated_users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    
    @validates('username')
    def validate_username(self, key, username):
        """Validate username before saving"""
        # key = 'username'
        # username = value being set
        
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        
        if not username.isalnum():
            raise ValueError("Username must be alphanumeric")
        
        # Return the (possibly modified) value
        return username.lower()  # Normalize to lowercase
    
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format"""
        if '@' not in email:
            raise ValueError("Invalid email format")
        return email.lower()
    
    @validates('age')
    def validate_age(self, key, age):
        """Validate age is reasonable"""
        if age < 0 or age > 150:
            raise ValueError("Age must be between 0 and 150")
        return age


# ============================================================
# 7️⃣ COMPUTED PROPERTIES — HYBRID PROPERTIES
# ============================================================
"""
hybrid_property = Python property that can also work in SQL queries

WHAT STAYS IN PYTHON:
• The @hybrid_property getter - Called when accessing obj.full_name
• The @full_name.expression - SQL expression for queries

WHAT REACHES DATABASE:
• Nothing by default (computed on the fly)
• OR the SQL expression when used in queries
"""

class Person(Base):
    """Model with computed properties"""
    
    __tablename__ = "people"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    
    @hybrid_property
    def full_name(self) -> str:
        """Python-side: Concatenate first + last name"""
        return f"{self.first_name} {self.last_name}"
    
    @full_name.expression
    def full_name(cls):
        """SQL-side: Database concatenation for queries"""
        return cls.first_name + ' ' + cls.last_name
    
    @hybrid_property
    def is_adult(self) -> bool:
        """Example of boolean computed property"""
        # You'd need an age column for this to make sense
        return True  # Simplified example
    
    # Hybrid method - accepts arguments
    @hybrid_method
    def has_name_like(self, pattern: str) -> bool:
        """Python-side check"""
        return pattern.lower() in self.full_name.lower()
    
    @has_name_like.expression
    def has_name_like(cls, pattern):
        """SQL-side check for queries"""
        return cls.full_name.ilike(f'%{pattern}%')


"""
USAGE:

person = Person(first_name="John", last_name="Doe")

# Python-side (uses @hybrid_property)
print(person.full_name)  # "John Doe"

# SQL-side (uses @full_name.expression)
from sqlalchemy import select
stmt = select(Person).where(Person.full_name == "John Doe")
"""


# ============================================================
# 8️⃣ INDEXES — PERFORMANCE OPTIMIZATION
# ============================================================
"""
Indexes speed up queries but slow down writes.

WHAT REACHES DATABASE:
• Index definitions - CREATE INDEX statements
• Unique indexes - Created with unique=True

WHAT STAYS IN PYTHON:
• Index names (unless specified)
• Index configuration
"""

class IndexedModel(Base):
    """Model with various index types"""
    
    __tablename__ = "indexed_models"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Single column index
    # Database: CREATE INDEX ix_indexed_models_email ON indexed_models(email)
    email: Mapped[str] = mapped_column(
        String(100),
        index=True  # ← Creates index in DB
    )
    
    # Unique index (also enforces uniqueness)
    # Database: CREATE UNIQUE INDEX ix_username ON indexed_models(username)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,  # ← Creates unique index
        index=True
    )
    
    # Index with specific name
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        index=Index("idx_user_phone", "phone")  # Custom name
    )
    
    # Composite index (multiple columns)
    # Defined in __table_args__ below
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    
    # Partial index (index only some rows)
    # Defined in __table_args__ below
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    __table_args__ = (
        # Composite index on (first_name, last_name)
        Index('idx_full_name', 'first_name', 'last_name'),
        
        # Partial index - only index active users
        Index('idx_active_users', 'email', postgresql_where=(status == 'active')),
        
        # Table comment (PostgreSQL)
        {'comment': 'Table for demonstrating indexes'}
    )


# ============================================================
# 9️⃣ TABLE CONFIGURATION — __table_args__
============================================================
"""
__table_args__ = Additional table-level configuration

WHAT REACHES DATABASE:
• Constraints (UniqueConstraint, CheckConstraint, ForeignKeyConstraint)
• Indexes (Index)
• Schema name
• Table comments

WHAT STAYS IN PYTHON:
• Polymorphic settings (for inheritance)
"""

class ConfiguredModel(Base):
    """Model with table-level configuration"""
    
    __tablename__ = "configured_models"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Columns for constraints
    code: Mapped[str] = mapped_column(String(10))
    region: Mapped[str] = mapped_column(String(10))
    year: Mapped[int] = mapped_column(Integer)
    
    # Columns for composite FK
    ref_code: Mapped[str] = mapped_column(String(10))
    ref_region: Mapped[str] = mapped_column(String(10))
    
    __table_args__ = (
        # Composite unique constraint
        # Database: UNIQUE (code, region)
        UniqueConstraint('code', 'region', name='uq_code_region'),
        
        # Check constraint
        # Database: CHECK (year >= 1900 AND year <= 2100)
        CheckConstraint('year >= 1900 AND year <= 2100', name='check_year'),
        
        # Composite foreign key
        # Database: FOREIGN KEY (ref_code, ref_region) REFERENCES other(code, region)
        # ForeignKeyConstraint(
        #     ['ref_code', 'ref_region'],
        #     ['other.code', 'other.region'],
        #     name='fk_ref'
        # ),
        
        # Index
        Index('idx_code', 'code'),
        
        # Schema (PostgreSQL schemas)
        # {'schema': 'my_schema'}
        
        # Table comment
        {'comment': 'Model demonstrating table-level config'}
    )


# ============================================================
# 10️⃣ MIXINS — REUSABLE MODEL COMPONENTS
# ============================================================
"""
Mixins = Classes that provide reusable columns/methods

WHAT REACHES DATABASE:
• Columns defined in mixin (same as any column)
• Constraints defined in mixin

WHAT STAYS IN PYTHON:
• Methods defined in mixin
• Class-level configuration
"""

class TimestampMixin:
    """Adds created_at and updated_at to any model"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,  # ← Auto-update on change
        nullable=False
    )


class AuditMixin:
    """Adds audit fields to any model"""
    
    created_by: Mapped[Optional[str]] = mapped_column(String(50))
    updated_by: Mapped[Optional[str]] = mapped_column(String(50))
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Auto-generate table name from class name"""
        return cls.__name__.lower() + 's'


class SoftDeleteMixin:
    """Adds soft delete capability"""
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    def soft_delete(self):
        """Mark as deleted without removing from DB"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None


# Using mixins
class Product(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    """Product model with all mixins"""
    
    # __tablename__ auto-generated by AuditMixin: "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    # Inherits from TimestampMixin:
    # - created_at
    # - updated_at
    
    # Inherits from AuditMixin:
    # - created_by
    # - updated_by
    
    # Inherits from SoftDeleteMixin:
    # - is_deleted
    # - deleted_at
    # - soft_delete()
    # - restore()


"""
WHAT REACHES DATABASE for Product:
Table: products
Columns:
  - id (PK)
  - name
  - price
  - created_at (from TimestampMixin)
  - updated_at (from TimestampMixin)
  - created_by (from AuditMixin)
  - updated_by (from AuditMixin)
  - is_deleted (from SoftDeleteMixin)
  - deleted_at (from SoftDeleteMixin)
"""


# ============================================================
# 11️⃣ ADVANCED COLUMN CONFIGURATIONS
# ============================================================

# Enum handling
class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class ModelWithEnum(Base):
    """Using Python enums in models"""
    
    __tablename__ = "enum_models"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Enum stored as ENUM type in PostgreSQL
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER
    )
    
    # Enum stored as VARCHAR (more portable)
    role_as_string: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.USER
    )


# Column with sort order
class SortedModel(Base):
    """Model with sortable items"""
    
    __tablename__ = "sorted_models"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # Sort order field
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True  # Good for sorting
    )
    
    __table_args__ = (
        # Ensure sort_order is unique (no duplicates)
        UniqueConstraint('sort_order', name='uq_sort_order'),
    )


# Auto-increment with custom start
class SequentialModel(Base):
    """Model with auto-numbering"""
    
    __tablename__ = "sequential_models"
    
    # Serial/Auto-increment
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    # Custom sequence (PostgreSQL)
    # order_number: Mapped[int] = mapped_column(
    #     Integer,
    #     Sequence('order_seq', start=1000),
    #     unique=True
    # )


# ============================================================
# 12️⃣ COMPLETE REAL-WORLD EXAMPLE
# ============================================================

class CompleteUser(TimestampMixin, Base):
    """
    Complete user model with all best practices
    
    WHAT REACHES DATABASE:
    - Table: complete_users
    - Columns: id, username, email, password_hash, is_active, 
               email_verified, created_at, updated_at
    - Constraints: PK on id, UNIQUE on username/email, 
                   CHECK on username length
    - Indexes: ix_complete_users_email, ix_complete_users_username
    - Foreign keys: None in this example
    
    WHAT STAYS IN PYTHON:
    - password property (setter validates, doesn't store plaintext)
    - Validation methods (@validates)
    - is_password_valid method
    - __repr__ for debugging
    """
    
    __tablename__ = "complete_users"
    
    # Primary key - auto-increment
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    # Username with validation
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    
    # Email with validation  
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    
    # Password hash (never store plaintext!)
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Status flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Table-level constraints
    __table_args__ = (
        CheckConstraint(
            "LENGTH(username) >= 3",
            name="check_username_length"
        ),
        Index('ix_active_users', 'is_active', 'created_at'),
    )
    
    # Validation
    @validates('username')
    def validate_username(self, key, value):
        if len(value) < 3:
            raise ValueError("Username too short")
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        return value.lower()
    
    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError("Invalid email")
        return value.lower()
    
    # Password handling (Python-only, not a column)
    @property
    def password(self):
        """Raise error if trying to read password"""
        raise AttributeError("Password is not readable")
    
    @password.setter
    def password(self, plaintext: str):
        """Hash and store password"""
        if len(plaintext) < 8:
            raise ValueError("Password must be 8+ characters")
        # In real app: use bcrypt, argon2, etc.
        import hashlib
        self.password_hash = hashlib.sha256(plaintext.encode()).hexdigest()
    
    def is_password_valid(self, plaintext: str) -> bool:
        """Check if password matches"""
        import hashlib
        hash_check = hashlib.sha256(plaintext.encode()).hexdigest()
        return hash_check == self.password_hash
    
    def __repr__(self) -> str:
        return f"<CompleteUser(id={self.id}, username='{self.username}')>"


# ============================================================
# 13️⃣ DATABASE SCHEMA GENERATION
# ============================================================
"""
Create all tables defined in your models
"""

def create_tables():
    """Create all tables in the database"""
    engine = create_engine(
        "postgresql+psycopg2://postgres:1729@localhost:5432/newdb",
        echo=True  # Print SQL statements
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Tables created successfully!")
    
    # To drop all tables:
    # Base.metadata.drop_all(engine)


def show_table_info():
    """Display information about all tables"""
    for table_name, table in Base.metadata.tables.items():
        print(f"\n{'='*50}")
        print(f"Table: {table_name}")
        print(f"{'='*50}")
        
        print("Columns:")
        for column in table.columns:
            constraints = []
            if column.primary_key:
                constraints.append("PK")
            if not column.nullable:
                constraints.append("NOT NULL")
            if column.unique:
                constraints.append("UNIQUE")
            if column.default:
                constraints.append(f"DEFAULT: {column.default}")
            
            constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
            print(f"  - {column.name}: {column.type}{constraint_str}")
        
        print("\nConstraints:")
        for constraint in table.constraints:
            print(f"  - {constraint}")
        
        print("\nIndexes:")
        for index in table.indexes:
            print(f"  - {index.name}: {', '.join(c.name for c in index.columns)}")


if __name__ == "__main__":
    show_table_info()
    # create_tables()


# ============================================================
# 14️⃣ QUICK REFERENCE CHEAT SHEET
# ============================================================
"""
QUICK REFERENCE
===============

BASIC MODEL:
------------
class MyModel(Base):
    __tablename__ = "my_models"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


COLUMN TYPES:
-------------
Integer, String(length), Text, Boolean
DateTime, Date, Time, Numeric(precision, scale), Float
LargeBinary (for files), JSON (for flexible data), UUID
Enum(PythonEnum), ARRAY (PostgreSQL), JSONB (PostgreSQL)


CONSTRAINTS:
------------
primary_key=True
nullable=False (NOT NULL) / nullable=True (NULL allowed)
unique=True
index=True
default=python_value
server_default=text("SQL_EXPR")
autoincrement=True


FOREIGN KEY:
------------
column_id: Mapped[int] = mapped_column(
    ForeignKey(
        "other_table.id",
        ondelete="CASCADE|SET NULL|RESTRICT",
        onupdate="CASCADE"
    )
)


VALIDATION:
-----------
@validates('field_name')
def validate_field(self, key, value):
    if not valid:
        raise ValueError("Invalid")
    return normalized_value


HYBRID PROPERTY:
----------------
@hybrid_property
def full_name(self):
    return self.first + ' ' + self.last

@full_name.expression
def full_name(cls):
    return cls.first + ' ' + cls.last


INDEXES:
--------
# Single column
email: Mapped[str] = mapped_column(String(100), index=True)

# Composite in __table_args__
__table_args__ = (
    Index('idx_name', 'col1', 'col2'),
)


TABLE ARGS:
-----------
__table_args__ = (
    UniqueConstraint('col1', 'col2', name='uq_name'),
    CheckConstraint('age >= 0', name='check_age'),
    Index('idx_name', 'col'),
    {'schema': 'my_schema', 'comment': 'Table description'}
)


MIXINS:
-------
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

class MyModel(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True)


PYTHON vs DATABASE:
-------------------
PYTHON-ONLY (not in DB):
  - @validates methods
  - @hybrid_property (unless used in query)
  - Regular @property
  - Instance methods
  - Class methods
  - __repr__, __str__

REACHES DATABASE:
  - __tablename__
  - Column definitions (name, type, constraints)
  - ForeignKey constraints
  - Index definitions
  - Table constraints (UniqueConstraint, CheckConstraint)
  - server_default values (SQL expressions)
  - __table_args__ settings
"""
