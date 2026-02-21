#we are defining our sqlalchemy ORM models
from datetime import datetime

from sqlalchemy import String , func
from sqlalchemy.orm import DeclarativeBase , Mapped , mapped_column


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(primary_key=True , index=True )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email : Mapped[str] = mapped_column(String(255) , unique=True , nullable=False)

