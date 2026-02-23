from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_models import InvoiceResponse, InvoiceCreate, InvoiceUpdate
from database_config import get_db
from invoice_repository import InvoiceRepository

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice_router(invoice_create: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    invoice_repo = InvoiceRepository(db)
    invoice = await invoice_repo.create_invoice(invoice_create)
    return invoice

@router.delete("/{invoice_id}")
async def delete_invoice( invoice_id:int, db: AsyncSession = Depends(get_db)):
    invoice_repo = InvoiceRepository(db)
    invoice = await invoice_repo.delete_invoice(invoice_id)
    return invoice

@router.get("/")
async def get_all_invoices(
        skip :int = 0,
        limit:int = 10,
        db: AsyncSession = Depends(get_db)
):
    invoice_repo = InvoiceRepository(db)
    invoices = await invoice_repo.get_all_invoices(skip=skip, limit=limit)
    return invoices
