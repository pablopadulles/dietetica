from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from models.database import db
from models.movimiento import MovimientoCreate, MovimientoUpdate, MovimientoResponse

router = APIRouter(
    prefix="/movimientos",
    tags=["movimientos"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=MovimientoResponse, status_code=status.HTTP_201_CREATED)
async def create_movimiento(movimiento: MovimientoCreate):
    # Validar depósito origen
    if movimiento.origen_id:
        if not ObjectId.is_valid(movimiento.origen_id):
             raise HTTPException(status_code=400, detail="ID de depósito origen inválido")
        deposito_origen = await db.depositos_collection.find_one({"_id": ObjectId(movimiento.origen_id)})
        if not deposito_origen:
             raise HTTPException(status_code=400, detail="Depósito origen no encontrado")
             
    # Validar depósito destino
    if movimiento.destino_id:
        if not ObjectId.is_valid(movimiento.destino_id):
             raise HTTPException(status_code=400, detail="ID de depósito destino inválido")
        deposito_destino = await db.depositos_collection.find_one({"_id": ObjectId(movimiento.destino_id)})
        if not deposito_destino:
             raise HTTPException(status_code=400, detail="Depósito destino no encontrado")

    nuevo_movimiento = movimiento.model_dump()
    result = await db.movimientos_collection.insert_one(nuevo_movimiento)
    created_movimiento = await db.movimientos_collection.find_one({"_id": result.inserted_id})
    if created_movimiento:
        created_movimiento["id"] = str(created_movimiento["_id"])
        return created_movimiento
    raise HTTPException(status_code=500, detail="Error al crear el movimiento")

@router.get("/", response_model=List[MovimientoResponse])
async def read_movimientos():
    movimientos = []
    async for mov in db.movimientos_collection.find():
        mov["id"] = str(mov["_id"])
        movimientos.append(mov)
    return movimientos

@router.get("/{id}", response_model=MovimientoResponse)
async def read_movimiento(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    movimiento = await db.movimientos_collection.find_one({"_id": ObjectId(id)})
    if movimiento is None:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    movimiento["id"] = str(movimiento["_id"])
    return movimiento

@router.put("/{id}", response_model=MovimientoResponse)
async def update_movimiento(id: str, movimiento_update: MovimientoUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in movimiento_update.model_dump().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await db.movimientos_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if update_result.modified_count == 0 and update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
            
    if (updated_movimiento := await db.movimientos_collection.find_one({"_id": ObjectId(id)})) is not None:
        updated_movimiento["id"] = str(updated_movimiento["_id"])
        return updated_movimiento
        
    raise HTTPException(status_code=404, detail="Movimiento no encontrado")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movimiento(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
        
    delete_result = await db.movimientos_collection.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
