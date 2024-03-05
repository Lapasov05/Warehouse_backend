from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from Orders.scheme import Get_orders, Get_shopping_carts
from auth.utills import verify_token
from database import get_async_session
from models.models import User, Customer, Order, Product, Shopping_cart, Debts

order_root = APIRouter()


@order_root.post('/order/add')
async def add_order(customer_id: int,
                    token: dict = Depends(verify_token),
                    session: AsyncSession = Depends(get_async_session)
                    ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query_cutomer = select(Customer).where(Customer.id == customer_id)
            res_customer = await session.execute(query_cutomer)
            if res_customer.scalar():
                query = insert(Order).values(customer_id=customer_id, user_id=user_id)
                await session.execute(query)
                await session.commit()
                return HTTPException(status_code=200, detail="Customer added!")
            else:
                return HTTPException(status_code=405, detail="Customer not found")
        else:
            return HTTPException(status_code=405, detail="Not allowed")


@order_root.get('/order/get', response_model=List[Get_orders])
async def get_orders(token: dict = Depends(verify_token),
                     session: AsyncSession = Depends(get_async_session)
                     ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = select(Order)
            res = await session.execute(query)
            result = res.scalars().all()
            return result


@order_root.post('/shopping_cart/add')
async def add_shopping_cart(order_id: int,
                            product_id: int,
                            amount: int,
                            token: dict = Depends(verify_token),
                            session: AsyncSession = Depends(get_async_session)
                            ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query_customer = select(Order).where(Order.id == order_id)
            res_customer = await session.execute(query_customer)
            result_customer = res_customer.scalar()
            if result_customer:
                query_product = select(Product).where(Product.id == product_id and Product.amount <= amount)
                res_product = await session.execute(query_product)
                result_product = res_product.scalar()
                if result_product:
                    total = result_product.price * amount
                    query_insert = insert(Shopping_cart).values(order_id=order_id, product_id=product_id,
                                                                amount=amount, total=total, is_active=True)
                    await session.execute(query_insert)
                    await session.commit()
                    return {"success": True, "message": "Added successfully"}
                else:
                    return HTTPException(status_code=405, detail="Product not found or amount is not enough")
            else:
                return HTTPException(status_code=404, detail="Customer not found")
        else:
            return HTTPException(status_code=405, detail="Not allowed")


@order_root.get('/shopping_cart/get', response_model=List[Get_shopping_carts])
async def get_shopping_cart(token: dict = Depends(verify_token),
                            session: AsyncSession = Depends(get_async_session)
                            ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query_shop = select(Shopping_cart)
            res_shop = await session.execute(query_shop)
            result_shop = res_shop.scalars().all()
            return result_shop
        else:
            return HTTPException(status_code=405, detail="Not allowed")


@order_root.post('/debts/add')
async def add_order_shopping_cart(order_id: int,
                                  paid: float,
                                  token: dict = Depends(verify_token),
                                  session: AsyncSession = Depends(get_async_session)
                                  ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query_shopping_cart = select(Shopping_cart).where(
                Shopping_cart.order_id == order_id and Shopping_cart.is_active == True)
            res_shopping_cart = await session.execute(query_shopping_cart)
            result_shopping_cart = res_shopping_cart.scalars().all()
            if result_shopping_cart:
                total = 0
                for cart in result_shopping_cart:
                    total += cart.total

                should_pay = total - paid
                query_insert = insert(Debts).values(order_id=order_id, paid=paid, should_pay=should_pay, total=total)
                await session.execute(query_insert)
                for cart in result_shopping_cart:
                    query_update = update(Shopping_cart).where(Shopping_cart.id == cart.id).values(is_active=False)
                    query_change = update(Product).where(Product.id == cart.product_id).values(
                        amount=Product.amount - cart.amount)
                    await session.execute(query_change)
                    await session.execute(query_update)

                await session.commit()
                return HTTPException(status_code=200, detail="Debt added!")
            else:
                return HTTPException(status_code=404,detail="Not found")



