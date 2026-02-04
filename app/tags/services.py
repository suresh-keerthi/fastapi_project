from typing import List
from sqlmodel import Session, select
from app.db.models import Tag, BookTagLink, Book

async def read_all_tags(session: Session) -> List[Tag]:
    statement = select(Tag)
    tags = session.exec(statement).all()
    return tags

async def create_new_tags(session: Session, tag_names: List[str]) -> List[Tag]:
    #check if tag already exists if not create new
    created_tags = []
    for name in tag_names:
        existing_tag = session.exec(select(Tag).where(Tag.name == name)).first()
        if existing_tag:
            created_tags.append(existing_tag)
        else:
            new_tag = Tag(name=name)
            session.add(new_tag)
            await session.commit()
            await session.refresh(new_tag)
            created_tags.append(new_tag)

    return created_tags


async def add_tags_to_user_book(session: Session, book_uid: str,user_uid: str, tag_names: List[str]) -> List[BookTagLink]:
    #check if book exists and  it is owned by the user
    book = session.exec(select(Book).where(Book.uid == book_uid)).first()
    if (book.user_uid != user_uid):
        return []
    if not book:
        return []
    book_tag_links = []
    for name in tag_names:
        tag = session.exec(select(Tag).where(Tag.name == name)).first()
        if tag:
            link = BookTagLink(book_uid=book.uid, tag_uid=tag.uid)
            session.add(link)
            book_tag_links.append(link)
    await session.commit()
    return book_tag_links
 

    

async def delete_tag(session: Session, tag_name: str) -> bool:
    tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
    if not tag:
        return False
    # Remove all associated BookTagLink entries
    book_tag_links = session.exec(select(BookTagLink).where(BookTagLink.tag_uid == tag.uid)).all()
    for link in book_tag_links:
        session.delete(link)
    # Delete the tag itself
    session.delete(tag)
    await session.commit()
    return True

