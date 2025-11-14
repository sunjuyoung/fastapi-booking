from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select, func
from appserver.db import DbSessionDep
from .models import User
from .exceptions import DuplicatedUsernameError, DuplicatedEmailError, UserNotFoundError, PasswordMismatchError
from sqlalchemy.exc import IntegrityError
from .schemas import SignupPayload, UserOut, LoginPayload
from .utils import verify_password
from fastapi.responses import JSONResponse
from .utils import (
  verify_password,
  create_access_token,
  ACCESS_TOKEN_EXPIRE_MINUTES
)



router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.get("/users/{username}")
async def user_detail(username: str, session: DbSessionDep) -> User:
  stmt = select(User).where(User.username == username)
  result = await session.execute(stmt)
  user = result.scalar_one_or_none()
  
  if user is not None:
    return user

    
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


#model_validate 는 pydantic 제공하는 함수로 ,해당 모델필드의 유효성 검사를 검증한 후 객체를 반환합니다.
#dic 자료형이 아닐경우 , 속성으로 접근해야 하는 객체일때는 from_attributes=True 옵션을 추가해야 합니다.
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def signup(payload: SignupPayload, session: DbSessionDep) -> User:
  stmt = select(func.count()).select_from(User).where(User.username == payload.username)
  
  result = await session.execute(stmt)
  count = result.scalar_one()
  if count > 0:
    raise DuplicatedUsernameError
  

  user = User.model_validate(payload)
  session.add(user)
  
  try:
    await session.commit()
  except IntegrityError as e:
    raise DuplicatedEmailError
  
  return user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: LoginPayload, session: DbSessionDep) -> User:
  stmt = select(User).where(User.username == payload.username)
  result = await session.execute(stmt)
  user = result.scalar_one_or_none()
  
  if user is None:
    raise UserNotFoundError
  
  if not verify_password(payload.password, user.hashed_password):
    raise PasswordMismatchError
  
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
    data={
      "sub": user.username,
      "display_name": user.display_name,
      "is_host": user.is_host,
    },
    expires_delta=access_token_expires
  )
  
  response_data = {
    
      "access_token": access_token,
      "token_type": "bearer",
      "user": user.model_dump(mode="json", exclude={"hashed_password", "email"}),
    }
  
  
  now = datetime.now(timezone.utc)
  
  res = JSONResponse(response_data, status_code=status.HTTP_200_OK)
  
  res.set_cookie(
    key="auth_token",
    value=access_token,
    expires=now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    httponly=True,
    secure=True, 
    samesite="strict",
  )
  return res
  
  
  