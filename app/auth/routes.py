from fastapi import APIRouter,Depends,HTTPException, status
from app.auth.schemas import UserCreate, UserRead, UserLogin
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.main import get_session
from app.auth.services import AuthService
from app.auth.utils import create_tokens
from datetime import datetime, timedelta,timezone
from app.auth.dependencies import AccessTokenBearer, RefreshTokenBearer , get_curr_user
from app.auth.utils import black_list_jti
auth_service = AuthService()
router = APIRouter()

@router.post("/signup", response_model= UserRead, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, session : AsyncSession = Depends(get_session)):

    email = user_data.email
    # check if user with this email already exists
    user_exists  =  await auth_service.user_exists(email, session)
    if user_exists :
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, 
                            detail= "user with email already exists")

    try:
        user = await auth_service.create_user(user_data, session)
    except ValueError as exc:
        # propagation from password hashing (e.g. too long for bcrypt)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return user

@router.post("/login")
async def login(login_data : UserLogin, session : AsyncSession = Depends(get_session)):

    user  =  await auth_service.verify_login(login_data=login_data, session=session)
    if not user :
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= "invalid credentials")

    
    access_token = create_tokens(user_data={
        "uid": str(user.uid),
        "email": user.email,
        "username": user.username
    }, expiry= timedelta(minutes=15), refresh= False)

    refresh_token = create_tokens(user_data={
        "uid": str(user.uid),
        "email": user.email,
        "username": user.username
    }, expiry= timedelta(days=7), refresh= True)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "message": "login successful",
        "user": {"uid": str(user.uid), "email": user.email, "username": user.username}
    }


@router.get("/me", response_model= UserRead)
async def get_me():
    pass

@router.get("/refresh_token")
async def refresh(payload: dict = Depends(RefreshTokenBearer(auto_error=True))):

    # we will get payload only if refresh token not expire so this exp checking is not requried
    exp  = payload["expiry"]
    curr = int(datetime.now(timezone.utc).timestamp()) 
    if curr >= exp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="token expired")

    access_token = create_tokens(user_data=payload["user"], expiry=timedelta(minutes=15), refresh=False )

    return {
            "access_token": access_token
    }


@router.get("/logout")
async def logout(payload:dict = Depends(AccessTokenBearer(True))):
    jti = payload["jti"]
    print(jti)
    expiry = payload["exp"]
    await black_list_jti(jti, expiry)
    return {"message": "logged out successfully"}


     

     


    