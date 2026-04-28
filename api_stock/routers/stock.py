from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from bson import ObjectId
from models.database import db
import httpx
import os

router = APIRouter(
    prefix="/stock",
    tags=["stock"],
)

API_PRODUCTOS_URL = os.getenv("API_PRODUCTOS_URL", "http://api_productos:8000") # Asumiendo puerto de dev interno si no usa nginx interno, o simplemente el contenedor api_productos directo.

async def get_producto_por_id(producto_id: str):
    # En FastAPI, por defecto el puerto interno expuesto de uvicorn es 80, pero puede ser 8000, 8001 etc si configurado así.
    # Viendo docker-compose, el contenedor se llama api_productos, pero ¿en qué puerto corre internamente?
    # Usaremos http://api_productos/ (si corre por puerto 80) o http://api_productos:80. Si es necesario corregir, se ajustará.
    # Por defecto, la imagen FastAPI de tiangolo expone el puerto 80.
    async with httpx.AsyncClient() as client:
        try:
            # Quitamos el puerto fijo por defecto y probamos
            url = os.getenv("API_PRODUCTOS_URL", "http://api_productos/api")
            response = await client.get(f"{url}/productos/{producto_id}")
            if response.status_code == 200:
                return response.json()
        except httpx.RequestError as e:
            print(f"Error HTTP request: {e}")
            pass
    return None

async def calcular_stock_producto(producto_id: str) -> float:
    # Entradas: producto_id es el mismo y destino_id no es null (ingresó a un depósito)
    entradas = db.movimientos_collection.aggregate([
        {"$match": {"producto_id": producto_id, "destino_id": {"$ne": None}}},
        {"$group": {"_id": "$producto_id", "total": {"$sum": "$cantidad"}}}
    ])
    total_entradas = 0.0
    async for entrada in entradas:
        total_entradas = entrada.get("total", 0.0)
        
    # Salidas: producto_id es el mismo y origen_id no es null (salió de un depósito)
    salidas = db.movimientos_collection.aggregate([
        {"$match": {"producto_id": producto_id, "origen_id": {"$ne": None}}},
        {"$group": {"_id": "$producto_id", "total": {"$sum": "$cantidad"}}}
    ])
    total_salidas = 0.0
    async for salida in salidas:
        total_salidas = salida.get("total", 0.0)
        
    return total_entradas - total_salidas

@router.get("/", response_model=Dict[str, float])
async def read_stock_general():
    """Devuelve el total de stock por cada producto_id"""
    entradas_cursor = db.movimientos_collection.aggregate([
        {"$match": {"destino_id": {"$ne": None}}},
        {"$group": {"_id": "$producto_id", "total": {"$sum": "$cantidad"}}}
    ])
    
    salidas_cursor = db.movimientos_collection.aggregate([
        {"$match": {"origen_id": {"$ne": None}}},
        {"$group": {"_id": "$producto_id", "total": {"$sum": "$cantidad"}}}
    ])
    
    stock_dict = {}
    async for entrada in entradas_cursor:
        prod_id = entrada["_id"]
        stock_dict[prod_id] = stock_dict.get(prod_id, 0.0) + entrada["total"]
        
    async for salida in salidas_cursor:
        prod_id = salida["_id"]
        stock_dict[prod_id] = stock_dict.get(prod_id, 0.0) - salida["total"]
        
    return stock_dict

@router.get("/producto/{id_o_nombre}")
async def read_stock_por_producto(id_o_nombre: str):
    """Calcula el stock de un producto por ID o Nombre."""
    producto = None
    
    # Intenta buscar por ID primero si parece un ID válido
    if ObjectId.is_valid(id_o_nombre):
         producto = await get_producto_por_id(id_o_nombre)
         
    # Si no es ID o no se encontró, busca por nombre
    if not producto:
        async with httpx.AsyncClient() as client:
            try:
                url = os.getenv("API_PRODUCTOS_URL", "http://api_productos/api")
                response = await client.get(f"{url}/productos/")
                if response.status_code == 200:
                    productos = response.json()
                    for p in productos:
                        if p.get("nombre", "").lower() == id_o_nombre.lower() or p.get("id") == id_o_nombre:
                            producto = p
                            break
            except httpx.RequestError as e:
                print(f"Error HTTP request: {e}")
                pass
                
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    producto_id = producto["id"]
    stock_total = await calcular_stock_producto(producto_id)
    
    return {
        "producto": producto,
        "stock": stock_total
    }
