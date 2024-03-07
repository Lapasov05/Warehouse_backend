from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from auth.utills import verify_token
from database import get_async_session
from models.models import Warehouse, Warehouse_category, Product, User, Product_History, Product_location
from warehouse.scheme import Add_warehouse, Get_warehouse, Product_history

warehouse_root = APIRouter()


@warehouse_root.post("/warehouse/add")
async def add_warehouse(model: Add_warehouse,
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
            return HTTPException(status_code=200, detail=" Warehouse added")


@warehouse_root.get('/warehouse/get', response_model=List[Get_warehouse])
async def get_warehouse(token: dict = Depends(verify_token),
                        session: AsyncSession = Depends(get_async_session)
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
async def add_category_warehouse(warehouse_id: int,
                                 category_id: int,
                                 token: dict = Depends(verify_token),
                                 session: AsyncSession = Depends(get_async_session)
                                 ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query_user = select(Warehouse_category).where(
                Warehouse_category.warehouse_id == warehouse_id and Warehouse_category.category_id == category_id)
            res = await session.execute(query_user)
            if not res.scalar():
                query = insert(Warehouse_category).values(warehouse_id=warehouse_id, category_id=category_id)
                await session.execute(query)
                await session.commit()
                return HTTPException(status_code=200, detail=" Warehouse_Category added")
            else:
                return HTTPException(status_code=400, detail="Already added!")


@warehouse_root.get('warehouse/Category/get', response_model=List[Get_warehouse])
async def get_warehouse(token: dict = Depends(verify_token),
                        session: AsyncSession = Depends(get_async_session)
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
async def get_warehouse_products(warehouse_id: int,
                                 token: dict = Depends(verify_token),
                                 session: AsyncSession = Depends(get_async_session)
                                 ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = select(Product).where(Product.warehouse_id == warehouse_id)
            res = await session.execute(query)
            result = res.scalars().all()
            return result


from sqlalchemy.exc import IntegrityError

@warehouse_root.post('/warehouse/Carry_product')
async def change_location(primary_warehouse: int,
                          next_warehouse: int,
                          product_id: int,
                          amount: int,
                          token: dict = Depends(verify_token),
                          session: AsyncSession = Depends(get_async_session)
                          ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id, User.role_id == 1)
        res_user = await session.execute(query_user)

        if res_user.scalar():
            # Check if the product exists in the current warehouse with enough amount
            query_check_old = select(Product_location).where(
                Product_location.product_id == product_id,
                Product_location.warehouse_id == primary_warehouse,
                Product_location.amount >= amount
            )
            result_primary = await session.execute(query_check_old)
            result_primary = result_primary.scalars().first()

            # Check if the product exists in the next warehouse
            query_check_new = select(Product_location).where(
                Product_location.product_id == product_id,
                Product_location.warehouse_id == next_warehouse
            )
            result_next = await session.execute(query_check_new)
            result_next = result_next.scalars().first()
            print(result_primary.amount)
            if result_primary.amount > amount:
                if result_primary and result_next and result_primary.amount >= amount:
                    new_amount = result_next.amount + amount

                    # Update the amount in the next warehouse
                    query_update_next = update(Product_location).where(
                        (Product_location.product_id == product_id) &
                        (Product_location.warehouse_id == next_warehouse)
                    ).values(
                        amount=new_amount
                    )

                    # Update the amount in the current warehouse
                    query_update_old = update(Product_location).where(
                        (Product_location.product_id == product_id) &
                        (Product_location.warehouse_id == primary_warehouse)
                    ).values(
                        amount=result_primary.amount - amount
                    )
                    query_insert_history = insert(Product_History).values(primary_warehouse=primary_warehouse,
                                                                          next_warehouse=next_warehouse,
                                                                          product_id=product_id,
                                                                          count=amount
                                                                          )
                    await session.execute(query_insert_history)

                    try:
                        # Execute both update queries
                        await session.execute(query_update_next)
                        await session.execute(query_update_old)
                        await session.commit()
                        return HTTPException(status_code=200, detail="Product location changed!")
                    except IntegrityError:
                        await session.rollback()
                        return HTTPException(status_code=500, detail="Integrity Error")

                else:
                    try:
                        # If the product doesn't exist in the current warehouse, insert into the next warehouse
                        query_insert_next = insert(Product_location).values(
                            product_id=product_id, warehouse_id=next_warehouse, amount=amount
                        )
                        await session.execute(query_insert_next)

                        # Update the amount in the current warehouse
                        query_update_old = update(Product_location).where(
                            (Product_location.product_id == product_id) &
                            (Product_location.warehouse_id == primary_warehouse)
                        ).values(
                            amount=result_primary.amount - amount
                        )
                        query_insert_history = insert(Product_History).values(primary_warehouse=primary_warehouse,
                                                                              next_warehouse=next_warehouse,
                                                                              product_id=product_id,
                                                                              count=amount
                                                                              )
                        await session.execute(query_insert_history)

                        # Execute both queries
                        await session.execute(query_update_old)
                        await session.commit()
                        return HTTPException(status_code=200, detail="Product location changed!")

                    except IntegrityError:
                        await session.rollback()
                        return HTTPException(status_code=500, detail="Integrity Error")
            else:
                return HTTPException(status_code=500, detail="Warehouse do not have enough product ")
        else:
            return HTTPException(status_code=404, detail="User not authorized")


@warehouse_root.get('/warehouse/history', response_model=List[Product_history])
async def get_history(token: dict = Depends(verify_token),
                      session: AsyncSession = Depends(get_async_session)
                      ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(
            User.id == user_id and
            User.role_id == 1
        )
        res = await session.execute(query_user)
        if res.scalar():
            query_history = select(Product_History)
            res_history = await session.execute(query_history)
            result_history = res_history.scalars().all()
            list_result = []
            for item in result_history:
                query_warehouse_primary = select(Warehouse).where(Warehouse.id == item.primary_warehouse)
                warehouse_primary = await session.execute(query_warehouse_primary)
                warehouse_primary_detail = warehouse_primary.first()
                primary_warehouse_dict = {}
                if warehouse_primary_detail is not None:
                    primary_warehouse_dict = {
                        'id': warehouse_primary_detail[0].id,
                        'name': warehouse_primary_detail[0].name,
                        'latitude': warehouse_primary_detail[0].latitude,
                        'longitude': warehouse_primary_detail[0].longitude
                    }

                query_warehouse_next = select(Warehouse).where(Warehouse.id == item.next_warehouse)
                warehouse_next = await session.execute(query_warehouse_next)
                warehouse_next_detail = warehouse_next.first()
                next_warehouse_dict = {}
                if warehouse_next_detail is not None:
                    next_warehouse_dict = {
                        'id': warehouse_next_detail[0].id,
                        'name': warehouse_next_detail[0].name,
                        'latitude': warehouse_next_detail[0].latitude,
                        'longitude': warehouse_next_detail[0].longitude
                    }

                query_product = select(Product).where(Product.id == item.product_id)
                product_res = await session.execute(query_product)
                product_result = product_res.first()
                product_dict = {}
                if product_result is not None:
                    product_dict = {
                        'id': product_result[0].id,
                        'name': product_result[0].name,
                        'price': product_result[0].price,
                        'amount': product_result[0].amount,
                        'category_id': product_result[0].category_id,
                        'joined_at': product_result[0].joined_at,
                    }
                    list_result.append({
                        'id': item.id,
                        'primary_warehouse': primary_warehouse_dict,
                        'next_warehouse': next_warehouse_dict,
                        'product_id': product_dict,
                        'carried_at': item.carried_at
                    })

            return list_result
