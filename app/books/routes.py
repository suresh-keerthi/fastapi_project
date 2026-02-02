from fastapi import APIRouter, Depends, status, HTTPException
from app.db.main import get_session
from app.books.schemas import BookRead, BookUpdate, BookCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from uuid import UUID
from app.books import services
from app.auth.dependencies import RoleChecker, AccessTokenBearer
from app.db.models import Book

router = APIRouter()


@router.get(
    "/",
    response_model=List[BookRead],
    dependencies=[Depends(RoleChecker(["user", "admin"]))],
    status_code=status.HTTP_200_OK,
)
async def get_books(session: AsyncSession = Depends(get_session)):
    books = await services.get_books(session)
    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no books found"
        )
    return books



@router.get(
    "/my_books",
    response_model=List[BookRead],
    dependencies=[Depends(RoleChecker(["user", "admin"]))],
)
async def get_my_books(session: AsyncSession = Depends(get_session), payload: dict = Depends(AccessTokenBearer())):
    user_uid = payload["user"]["uid"]
    books = await services.get_books_by_user(session, user_uid)
    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no books found"
        )
    return books


@router.get(
    "/{book_id}",
    response_model=BookRead,
    dependencies=[Depends(RoleChecker(["user", "admin"]))],
)
async def get_book(book_id: UUID, seession: AsyncSession = Depends(get_session)):
    book = await services.get_book_by_id(book_id)
    return book


@router.post(
    "/",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["user", "admin"]))],
)
async def create_book(
    book_body: BookCreate,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(AccessTokenBearer()),
):
    user_uid = payload["user"]["uid"]
    return await services.create_book(user_uid, book_body, session)


@router.patch("/{book_id}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def update_book(
    book_id: UUID,
    book_body: BookUpdate,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(AccessTokenBearer()),
):

    book = await services.get_book_by_id(book_id, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalid book-id"
        )

    if book.user_uid != payload["user"]["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="only book owner is allowed to perform this",
        )

    updated_book = await services.update_book(book_id, book_body, session)
    return updated_book


@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
async def delete_book(
    book_id: UUID,
    session: AsyncSession = Depends(get_session),
    payload: dict = Depends(AccessTokenBearer()),
):
    book: Book = await services.get_book_by_id(book_id, session)
    if str(book.user_uid) != payload["user"]["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="only book owner is allowed to perform this",
        )

    deleted = await services.delete_book(book_id, session)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="invalid book-id"
        )
    return {"detail": "book deleted successfully"}
