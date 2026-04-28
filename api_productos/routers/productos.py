from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from models.database import db
from models.producto import ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter(
    prefix="/productos",
    tags=["productos"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(producto: ProductoCreate):
    nuevo_producto = producto.model_dump()
    result = await db.productos_collection.insert_one(nuevo_producto)
    created_producto = await db.productos_collection.find_one({"_id": result.inserted_id})
    if created_producto:
        created_producto["id"] = str(created_producto["_id"])
        return created_producto
    raise HTTPException(status_code=500, detail="Error al crear el producto")

@router.get("/", response_model=List[ProductoResponse])
async def read_productos():
    productos = []
    async for prod in db.productos_collection.find():
        prod["id"] = str(prod["_id"])
        productos.append(prod)
    return productos

@router.get("/{id}", response_model=ProductoResponse)
async def read_producto(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    producto = await db.productos_collection.find_one({"_id": ObjectId(id)})
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto["id"] = str(producto["_id"])
    return producto

@router.put("/{id}", response_model=ProductoResponse)
async def update_producto(id: str, producto_update: ProductoUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in producto_update.model_dump().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await db.productos_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        
        if update_result.modified_count == 0 and update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
    if (updated_producto := await db.productos_collection.find_one({"_id": ObjectId(id)})) is not None:
        updated_producto["id"] = str(updated_producto["_id"])
        return updated_producto
        
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_producto(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
        
    delete_result = await db.productos_collection.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.get("/cb/{codigo_barras}", response_model=ProductoResponse)
async def read_producto_codigo_barras(codigo_barras: str):
    producto = await db.productos_collection.find_one({"codigo_barras": codigo_barras})
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto["id"] = str(producto["_id"])
    return producto
