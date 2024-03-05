from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utills import verify_token
from database import get_async_session
from models.models import Product, Category, User
from product.scheme import Add_Product, Get_Products, Get_categories

product_root = APIRouter()


@product_root.post('/product/Add')
async def add_product(model: Add_Product,
                      token: dict = Depends(verify_token),
                      session: AsyncSession = Depends(get_async_session)):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id==user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = select(Category).where(Category.id == model.category_id)
            res = await session.execute(query)
            result = res.scalar()
            if result:
                query_insert = insert(Product).values(**dict(model))
                await session.execute(query_insert)
                await session.commit()
                return {"success": True, "detail": "Added successfully"}
            else:
                return HTTPException(status_code=404, detail="Category not found")
        else:
            return HTTPException(status_code=400,detail="Not allowed")

@product_root.get('/product/Get', response_model=List[Get_Products])
async def get_all_product(token: dict = Depends(verify_token),
                          session: AsyncSession = Depends(get_async_session)
                          ):
    if token is not None:
        query = select(Product)
        res = await session.execute(query)
        result = res.scalars().all()
        return result


@product_root.get('/product/category/get', response_model=List[Get_categories])
async def get_gategories(token: dict = Depends(verify_token),
                         session: AsyncSession = Depends(get_async_session)
                         ):
    if token is not None:
        query = select(Category)
        res = await session.execute(query)
        result = res.scalars().all()
        return result


@product_root.post('/product/category/post')
async def add_category(name: str,
                       token: dict = Depends(verify_token),
                       session: AsyncSession = Depends(get_async_session)
                       ):
    if token is not None:
        user_id = token.get('user_id')
        print(user_id)
        query_user = select(User).where(User.id==user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = insert(Category).values(name=name)
            await session.execute(query)
            await session.commit()
            return {"success": True, "detail": "Added category"}
        else:
            return HTTPException(status_code=400,detail="Not allowed")





