from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MovimientoBase(BaseModel):
    origen_id: Optional[str] = Field(None, description="ID del depósito de origen (vacío si es compra/ingreso)")
    destino_id: Optional[str] = Field(None, description="ID del depósito de destino (vacío si es venta/egreso)")
    producto_id: str = Field(..., description="ID del producto en api_productos")
    cantidad: float = Field(..., gt=0, description="Cantidad movida")
    fecha: datetime = Field(default_factory=datetime.utcnow)

class MovimientoCreate(MovimientoBase):
    pass

class MovimientoUpdate(BaseModel):
    origen_id: Optional[str] = None
    destino_id: Optional[str] = None
    producto_id: Optional[str] = None
    cantidad: Optional[float] = None
    fecha: Optional[datetime] = None

class MovimientoResponse(MovimientoBase):
    id: str

    class Config:
        from_attributes = True
