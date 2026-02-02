from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from datetime import datetime
from app.db.models import Book
from app.books.schemas import BookCreate, BookUpdate


async def get_books(session: AsyncSession) -> List[Book]:
    stmt = select(Book)
    results = await session.exec(stmt)
    return results.all()


async def get_books_by_user(session: AsyncSession, user_uid: UUID) -> List[Book]:
    stmt = select(Book).where(Book.user_uid == user_uid)
    results = await session.exec(stmt)
    return results.all()

async def create_book(user_uid : UUID, book_body: BookCreate, session: AsyncSession) -> Book:
    book_dict = book_body.model_dump()
    book = Book(**book_dict)
    book.user_uid = user_uid
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


async def get_book_by_id(book_id: UUID, session: AsyncSession) -> Optional[Book]:
    stmt = select(Book).where(Book.uid == book_id)
    result = await session.exec(stmt)
    return result.one_or_none()


async def update_book(book_id: UUID, book_body: BookUpdate, session: AsyncSession) -> Optional[Book]:
    book = await get_book_by_id(book_id, session)
    if book is None:
        return None

    book_update_dict = book_body.model_dump(exclude_unset=True)
    for k, v in book_update_dict.items():
        setattr(book, k, v)

    book.updated_at = datetime.now()
    await session.commit()
    await session.refresh(book)
    return book


async def delete_book(book_id: UUID, session: AsyncSession) -> bool:
    book = await get_book_by_id(book_id, session)
    if book is None:
        return False

    await session.delete(book)
    await session.commit()
    return True
