from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.db.models import User
from app.auth.schemas import UserCreate, UserLogin
from app.auth.utils import hash_password, verify_password
import uuid

class AuthService:
    async def get_user_by_email(self, email:str , session:AsyncSession ) -> User | None:  
        stmt =  select(User).where(User.email == email)
        result = await session.exec(stmt)
        user = result.one_or_none()
        return user
    
    async def get_user_by_uuid(self, uid: uuid.UUID, session: AsyncSession) -> User | None :
        stmt = select(User).where(User.uid == uid) 
        result = await session.exec(stmt)
        user = result.one_or_none()
        return user
    
    async def user_exists(self, email:str, session:AsyncSession):
        user = await self.get_user_by_email(email, session)
        return True if user else False
    
    async def create_user(self, user_data: UserCreate, session: AsyncSession):

        password = user_data.password
        hashed_pwd = await hash_password(password)
        user_data_dict = user_data.model_dump(exclude="password") 
        user = User(**user_data_dict)
        user.hashed_password = hashed_pwd
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user
    
    async def verify_login(self, login_data: UserLogin, session: AsyncSession) -> User:
        
        user = await self.get_user_by_email(login_data.email, session)
        if not user:
            return None        
        
        password_matched = await verify_password(
            login_data.password,
            user.hashed_password
        )

        if password_matched:
            return user       
        return None


                    

        

 
