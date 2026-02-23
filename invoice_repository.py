from typing import Any, Sequence

from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession

from api_models import InvoiceCreate, InvoiceUpdate
from models import Invoice


class InvoiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice(self, invoice_create: InvoiceCreate):
        invoice = Invoice(
            user_id= invoice_create.user_id,
            amount= invoice_create.amount,
            description= invoice_create.description
        )
        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

    async def get_invoice_by_id(self, id: int) -> Invoice:
        query = select(Invoice).where(Invoice.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_invoice_by_user_id(self, user_id: int) -> Invoice:
        query = select(Invoice).where(Invoice.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

