from fastapi import FastAPI
from invoice_routes import router as invoice_routes
from user_routes import router as user_router


app = FastAPI(
    title="CClarke ORM Implementation with DB Agent",
)

app.include_router(user_router)
app.include_router(invoice_routes)