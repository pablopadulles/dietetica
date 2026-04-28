from fastapi import FastAPI
import os
from models.database import db
from routers import productos

async def lifespan(app: FastAPI):
    # Connect to the database on startup
    db.connect()
    yield
    # Disconnect on shutdown
    db.disconnect()

app = FastAPI(
    title="API Productos",
    description="Microservicio de gestión de productos",
    version="1.0.0",
    root_path=os.getenv("ROOT_PATH", ""), 
    lifespan=lifespan
)

app.include_router(productos.router)