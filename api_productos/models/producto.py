from pydantic import BaseModel, Field
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str = Field(..., example="Yerba Mate")
    descripcion: Optional[str] = Field(None, example="Yerba mate de 1kg")
    precio: float = Field(..., example=1500.50)
    codigo_barras: Optional[str] = Field(None, example="7791234567890")

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    codigo_barras: Optional[str] = None

class ProductoResponse(ProductoBase):
    id: str

    class Config:
        from_attributes = True
