from fastapi import APIRouter, Depends,status, HTTPException
from app.db.models import Book
from app.db.main import get_session
from app.books.schemas import BookRead,BookUpdate ,BookCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from datetime import datetime
from typing import List


router = APIRouter()


@router.get("/",response_model=List[BookRead],status_code=status.HTTP_200_OK)
async def get_books( session:AsyncSession = Depends(get_session)):
    stmt =  select(Book)
    results = await session.exec(stmt)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail= "no books found")

    return  results.all()


@router.post("/", response_model = BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(book_body: BookCreate, session : AsyncSession = Depends(get_session)):
    book_dict = book_body.model_dump()
    book = Book(**book_dict)
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book
 
@router.patch("/{book_id}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def update_book(book_id: UUID , book_body:BookUpdate, session : AsyncSession = Depends(get_session)):
    stmt = select(Book).where(Book.uid == book_id)
    result = await session.exec(stmt)
    book = result.one_or_none()
    print(result,"/n", book , "suresh see here")

    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail= "invalid book-id")

    book_update_dict = book_body.model_dump(exclude_unset=True)

    for k, v in book_update_dict.items():
        setattr(book, k, v)
    
    book.updated_at = datetime.now()

    await session.commit()
    await session.refresh(book)
    return book


@router.delete("/{book_id}" , status_code=status.HTTP_200_OK )
async def delete_book( book_id: UUID , session : AsyncSession = Depends(get_session)):
    stmt = select(Book).where(Book.uid == book_id)
    result = await session.exec(stmt)
    book = result.one_or_none()

    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail= "invalid book-id")
    
    await session.delete(book)
    await session.commit()
    return {"detail" : "book deleted successfully"}

    

    






