from pydantic import BaseModel, Field
from typing import Optional

class DepositoBase(BaseModel):
    nombre: str = Field(..., example="Depósito Central")
    ubicacion: Optional[str] = Field(None, example="Av. Siempre Viva 123")

class DepositoCreate(DepositoBase):
    pass

class DepositoUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None

class DepositoResponse(DepositoBase):
    id: str

    class Config:
        from_attributes = True
