from sqlmodel.ext.asyncio.session import AsyncSession 
from sqlmodel import select
from app.db.models import Review
from typing import List
from app.reviews.schemas import ReviewCreate
from uuid import UUID  

async def get_all_reviews(session : AsyncSession) -> List[Review]:
    stmt = select(Review)
    result = await session.exec(stmt)
    reviews = result.all()
    return reviews

async def create_review_for_book(book_uid: UUID, user_uid : UUID, review_body: ReviewCreate, session : AsyncSession) -> Review:
    review = Review(**review_body.model_dump(), user_uid = user_uid, book_uid = book_uid)
    session.add(review)
    await session.commit()
    await session.refresh(review)
    return review

async def update_review_for_book(review_uid : UUID, user_uid : UUID, review_body : ReviewCreate, session : AsyncSession) -> Review | None:
    stmt = select(Review).where(Review.uid == review_uid, Review.user_uid == user_uid)
    result = await session.exec(stmt)
    review = result.one_or_none()
    if not review:
        return None
    if review:
        for key, value in review_body.model_dump(exclude_unset=True).items():
            setattr(review, key, value)
        session.add(review)
        await session.commit()
        await session.refresh(review)
    return review



async def delete_review_for_book(review_uid : UUID, user_uid : UUID, session : AsyncSession) -> bool:
    stmt = select(Review).where(Review.uid == review_uid, Review.user_uid == user_uid)
    result = await session.exec(stmt)
    review = result.one_or_none()
    if not review:
        return False
    await session.delete(review)
    await session.commit()
    return True