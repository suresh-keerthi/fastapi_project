from fastapi.security import HTTPBearer
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from app.auth.utils import decode_token, is_revoked
from typing import List
from app.auth.services import AuthService
from app.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import User

auth_service = AuthService()
security = HTTPBearer()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request):
        creds =  await super().__call__(request)

        payload = decode_token(creds.credentials)


        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
        
        #check if token is blacklisted
        revoked = await is_revoked(payload["jti"])
        if revoked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="token revoked login again")
        self.verify_token(payload)
        return payload
    
    def verify_token(self, payload: dict):
        pass


class AccessTokenBearer(TokenBearer): 
    def verify_token(self, payload: dict):
        if payload["refresh"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="access token required")


class RefreshTokenBearer(TokenBearer):
    def verify_token(self, payload):
        if not payload["refresh"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="refresh token requried")



async def get_curr_user(payload: dict = Depends(AccessTokenBearer()), session:AsyncSession= Depends(get_session)):
    uid = payload["user"]["uid"]
    user = await auth_service.get_user_by_uuid(uid, session)
    return user


#consider returning user, because sometimes i might have to call get_curr_user dependency again for user
class RoleChecker:
    def __init__(self ,allowed_roles:List[str]):
            self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_curr_user)):
        role = user.role
        if role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "you are not authorized")
            




        



    