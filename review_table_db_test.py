from app.db.models import Review
from app.db.main import get_session
import asyncio

async def main():
    agen = get_session()
    session = await agen.__anext__()
    review = Review( book_uid="6b6262c2-a797-45b4-98c5-598453d73e9c", user_uid="9dbe3d26-7130-4943-8047-2ee77b7528b4",
                    review_text="dirty book", rating = 3)


    session.add(review)
    await session.commit()
    await session.refresh(review) 
    print(review.model_dump())

    await agen.aclose()

    print("book name:",review.book.title, "reviewer:", review.user.username, "review:",review.review_text)


asyncio.run(main())