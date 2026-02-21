from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_models import UserCreate, UserResponse, UserUpdate
from database_config import get_db
from user_repository import UserRepository


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse , status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate ,
                      db : AsyncSession = Depends(get_db)):     #Dependency Injection

    user_repo = UserRepository(db)

    existing_user = await user_repo.get_user_by_email(user_create.email)
    if existing_user:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with Email already registered")

    user = await user_repo.create(user_create)
    return user

