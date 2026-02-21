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

@router.delete("/{user_id}",)
async def delete_user(user_id : int, db : AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)

    resp = await user_repo.delete_user(user_id)
    return resp

@router.get("/" , status_code=status.HTTP_200_OK)
async def get_all_users( db : AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)

    resp = await user_repo.get_all_users()
    return resp

