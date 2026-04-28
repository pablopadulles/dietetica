from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from models.database import db
from models.deposito import DepositoCreate, DepositoUpdate, DepositoResponse

router = APIRouter(
    prefix="/depositos",
    tags=["depositos"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=DepositoResponse, status_code=status.HTTP_201_CREATED)
async def create_deposito(deposito: DepositoCreate):
    nuevo_deposito = deposito.model_dump()
    result = await db.depositos_collection.insert_one(nuevo_deposito)
    created_deposito = await db.depositos_collection.find_one({"_id": result.inserted_id})
    if created_deposito:
        created_deposito["id"] = str(created_deposito["_id"])
        return created_deposito
    raise HTTPException(status_code=500, detail="Error al crear el depósito")

@router.get("/", response_model=List[DepositoResponse])
async def read_depositos():
    depositos = []
    async for dep in db.depositos_collection.find():
        dep["id"] = str(dep["_id"])
        depositos.append(dep)
    return depositos

@router.get("/{id}", response_model=DepositoResponse)
async def read_deposito(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    deposito = await db.depositos_collection.find_one({"_id": ObjectId(id)})
    if deposito is None:
        raise HTTPException(status_code=404, detail="Depósito no encontrado")
    deposito["id"] = str(deposito["_id"])
    return deposito

@router.put("/{id}", response_model=DepositoResponse)
async def update_deposito(id: str, deposito_update: DepositoUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in deposito_update.model_dump().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await db.depositos_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        
        if update_result.modified_count == 0 and update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Depósito no encontrado")
            
    if (updated_deposito := await db.depositos_collection.find_one({"_id": ObjectId(id)})) is not None:
        updated_deposito["id"] = str(updated_deposito["_id"])
        return updated_deposito
        
    raise HTTPException(status_code=404, detail="Depósito no encontrado")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deposito(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
        
    delete_result = await db.depositos_collection.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Depósito no encontrado")
