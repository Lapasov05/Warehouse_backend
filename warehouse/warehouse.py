from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from auth.utills import verify_token
from database import get_async_session
from models.models import Warehouse, Warehouse_category, Product, User
from warehouse.scheme import Add_warehouse, Get_warehouse

warehouse_root = APIRouter()


@warehouse_root.post("/warehouse/add")
async def add_warehouse(model:Add_warehouse,
                        token: dict = Depends(verify_token),
                        session: AsyncSession = Depends(get_async_session)
                        ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = insert(Warehouse).values(**dict(model))
            await session.execute(query)
            await session.commit()
            return HTTPException(status_code=200,detail=" Warehouse added")

@warehouse_root.get('warehouse/get',response_model=List[Get_warehouse])
async def get_warehouse(token:dict=Depends(verify_token),
                        session:AsyncSession = Depends(get_async_session)
                        ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = select(Warehouse)
            res = await session.execute(query)
            result = res.scalars().all()
            return result

@warehouse_root.post('warehouse/Category/add')
async def add_category_warehouse(warehouse_id:int,
                                 category_id:int,
                                 token:dict=Depends(verify_token),
                                 session:AsyncSession=Depends(get_async_session)
                                 ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = insert(Warehouse_category).values(warehouse_id=warehouse_id,category_id=category_id)
            await session.execute(query)
            await session.commit()
            return HTTPException(status_code=200,detail=" Warehouse_Category added")



@warehouse_root.get('warehouse/Category/get',response_model=List[Get_warehouse])
async def get_warehouse(token:dict=Depends(verify_token),
                        session:AsyncSession = Depends(get_async_session)
                        ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = select(Warehouse_category)
            res = await session.execute(query)
            result = res.scalars().all()
            return result



@warehouse_root.get("warehouse/Products")
async def get_warehouse_products(warehouse_id:int,
                                 token:dict=Depends(verify_token),
                                 session:AsyncSession=Depends(get_async_session)
                                 ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = select(Product).where(Product.warehouse_id==warehouse_id)
            res = await session.execute(query)
            result = res.scalars().all()
            return result

