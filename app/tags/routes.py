from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import Tag
from app.db.main import get_session
from app.tags.services import add_tags_to_user_book, read_all_tags, create_new_tags, delete_tag
from app.tags.schemas import TagRead, TagCreate, BookTagLinkRead
from app.auth.dependencies import RoleChecker, AccessTokenBearer
from typing import List

tags_router = APIRouter()


@tags_router.get("/", response_model=list[TagRead], dependencies=RoleChecker(required_roles=["user", "admin"]))
async def read_tags(session: AsyncSession = Depends(get_session)):
    tags = await read_all_tags(session)
    return tags


@tags_router.post(
    "/",
    response_model=List[TagRead],
    status_code=201,
    dependencies=[Depends(RoleChecker(required_roles=["admin"]))],
)
async def create_tags(
    tag: List[TagCreate], session: AsyncSession = Depends(get_session)
):
    tag_names = [t.name for t in tag]
    tags = await create_new_tags(session, tag_names)
    return tags


# user who is the owner of the book can add or remove tags to a particular book
#thoose tags must already exist in the tags table
@tags_router.post(
    "/assign/{book_uid}",
    response_model=List[BookTagLinkRead],
    status_code=200,
    dependencies=[Depends(RoleChecker(required_roles=["user", "admin"]))],
)
async def assign_tags_to_book(
    book_uid: str, tag: List[TagCreate], session: AsyncSession = Depends(get_session),
    payload: dict = Depends(AccessTokenBearer())
):
    user_uid = payload["user"]["uid"]
    tag_names = [t.name for t in tag]
    book_tag_links = await add_tags_to_user_book(session, book_uid, user_uid, tag_names)
    if not book_tag_links:
        raise HTTPException(status_code=404, detail="Book not found or not owned by user")
    return book_tag_links
  

#return books by tag name
# @tags_router.get("/books/{tag_name}", response_model=list[BookTag])



@tags_router.delete(
    "/{tag_name}",
    status_code=204,
    dependencies=[Depends(RoleChecker(required_roles=["admin"]))],
)
async def delete_tag(tag_name: str, session: AsyncSession = Depends(get_session)):
    success = await delete_tag(session, tag_name)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return None
