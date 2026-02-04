from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import RoleChecker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.main import get_session
from app.reviews.services import get_all_reviews, create_review_for_book, update_review_for_book, delete_review_for_book
from typing import List
from uuid import UUID
from app.auth.dependencies import AccessTokenBearer
from app.reviews.schemas import ReviewRead, ReviewCreate, ReviewUpdate

review_router = APIRouter()

# return all reviews of all books
# everything in the table
# user have to be authenticated to read reviews
# ( role checker  authenticates and then finds the role)
@review_router.get(
    "/",
    response_model=List[ReviewRead],
    dependencies=[Depends(RoleChecker(["user", "admin"]))],
)
async def get_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await get_all_reviews(session)
    return reviews

@review_router.post("/book/{book_uid}", response_model = ReviewRead)
async def create_review(book_uid : UUID, review_body : ReviewCreate, 
                        session: AsyncSession = Depends(get_session),
                        payload : dict = Depends(AccessTokenBearer())):
    user_uid = payload["user"]["uid"]
    review = await create_review_for_book(book_uid, user_uid, review_body, session)
    return review

@review_router.patch("/update/{review_uid}", response_model = ReviewRead, dependencies=[Depends(RoleChecker(["user", "admin"]))])
async def update_review(review_uid  : UUID, review_body : ReviewUpdate, 
                        session: AsyncSession = Depends(get_session),
                        payload : dict = Depends(AccessTokenBearer())):
    user_uid = payload["user"]["uid"]
    review = await update_review_for_book(review_uid, user_uid, review_body, session)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or not authorized to update")
    return review

@review_router.delete("/delete/{review_uid}", status_code = status.HTTP_204_NO_CONTENT,
                       dependencies=[Depends(RoleChecker(["user", "admin"]))])
async def delete_review(review_uid : UUID,
                        session: AsyncSession = Depends(get_session),
                        payload : dict = Depends(AccessTokenBearer())):
    user_uid = payload["user"]["uid"]
    success = await delete_review_for_book(review_uid, user_uid, session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or not authorized to delete")
    return {"message" : "Review deleted successfully"}





