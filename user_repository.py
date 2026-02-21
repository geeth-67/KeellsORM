from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_models import UserCreate, UserUpdate
from models import User


class UserRepository:

    def __init__(self , db: AsyncSession):
        self.db = db

    async def create(self, user_create: UserCreate):
        user = User(
            name=user_create.name,
            email=user_create.email
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self , email: str) -> User | None:

        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all_users(self , skip: int = 0, limit: int = 20) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_user_by_id(self , id: int) -> User | None:

        query = select(User).where(User.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def delete_user(self ,user_id: int):

        user = await self.get_user_by_id(user_id)

        if not user:
            return "user not found"

        await self.db.delete(user)
        await self.db.commit()
        return "User deleted successfully"

    async def update_user(self ,user_id : int, user_update: UserUpdate):

        user = await self.get_user_by_id(user_id )
        if not user:
            return "user not found"

        update_data = user_update.model_dump(exclude_unset=True)
        if update_data:
            for key, value in update_data.items():
                setattr(user, key, value)

            await self.db.commit()
            await self.db.refresh(user)

        return user