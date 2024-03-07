from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from Orders.scheme import Get_orders, Get_shopping_carts, Get_history
from auth.utills import verify_token
from database import get_async_session
from models.models import User, Customer, Order, Product, Shopping_cart, Debts, Product_History, Warehouse, \
    Product_location

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
            list_order = []
            for item in result:
                query_costumer = select(Customer).where(Customer.id == item.customer_id)
                res_cutomer = await session.execute(query_costumer)
                result_cutomer = res_cutomer.first()
                customer_dict = {}
                if result_cutomer is not None:
                    customer_dict = {
                        'id': result_cutomer[0].id,
                        'first_name': result_cutomer[0].first_name,
                        'last_name': result_cutomer[0].last_name,
                        'phone': result_cutomer[0].phone,
                        'email': result_cutomer[0].email
                    }
                query_user = select(User).where(User.id == item.user_id)
                res_user = await session.execute(query_user)
                result_user = res_user.first()
                user_dict = {}
                if result_user is not None:
                    user_dict = {
                        'id': result_user[0].id,
                        'first_name': result_user[0].first_name,
                        'last_name': result_user[0].last_name,
                        'username': result_user[0].username,
                        'email': result_user[0].email,
                        'phone': result_user[0].phone,
                    }
                list_order.append({
                    'id': item.id,
                    'customer_id': customer_dict,
                    'created_at': item.created_at,
                    'user_id': user_dict,
                    'is_active': item.is_active
                })
            return list_order


@order_root.post('/shopping_cart/add')
async def add_shopping_cart(order_id: int,
                            warehouse_id:int,
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
                query_product = select(Product).where(Product.id == product_id)
                query_Location_product =select(Product_location).where(Product_location.product_id== product_id and Product_location.warehouse_id == warehouse_id)
                res_location = await session.execute(query_Location_product)
                res_product = await session.execute(query_product)
                result_product = res_product.scalar()
                result_location = res_location.scalar()
                if result_product and result_location:
                    total = result_product.price * amount
                    query_insert = insert(Shopping_cart).values(order_id=order_id, product_id=product_id,
                                                                amount=amount,warehouse_id=warehouse_id, total=total, is_active=True)
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
            list_shopping_cart = []
            for item in result_shop:
                query_order = select(Order).where(Order.id == item.order_id)
                res_order = await session.execute(query_order)
                result_order = res_order.first()
                order_dict = {}
                if result_order is not None:
                    order_dict = {
                        'id': result_order[0].id,
                        'customer_id': result_order[0].customer_id,
                        'created_at': result_order[0].created_at,
                        'user_id': result_order[0].user_id,
                        'is_active': result_order[0].is_active
                    }
                query_product = select(Product).where(Product.id == item.product_id)
                res_product = await session.execute(query_product)
                result_product = res_product.first()
                product_dict = {}
                if result_product is not None:
                    product_dict = {
                        'id': result_product[0].id,
                        'name': result_product[0].name,
                        'price': result_product[0].price,
                        'amount': result_product[0].amount,
                        'category_id': result_product[0].category_id,
                        'joined_at': result_product[0].joined_at
                    }
                list_shopping_cart.append({
                    'id': item.id,
                    'order_id': order_dict,
                    'product_id': product_dict,
                    'amount': item.amount,
                    'total': item.total,
                    'is_active': item.is_active,
                })
            return list_shopping_cart
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
                    query_location_change = update(Product_location).where(Product_location.warehouse_id == cart.warehouse_id and Product_location.product_id == cart.product_id).values(
                        amount=Product_location.amount - cart.amount)
                    await session.execute(query_change)
                    await session.execute(query_update)
                    await session.execute(query_location_change)

                await session.commit()
                return HTTPException(status_code=200, detail="Debt added!")
            else:
                return HTTPException(status_code=404, detail="Not found")


@order_root.get("order/debts/get", response_model=List[Get_history])
async def get_debts(token: dict = Depends(verify_token),
                    session: AsyncSession = Depends(get_async_session)
                    ):
    if token is not None:
        user_id = token.get('user_id')
        query_user = select(User).where(User.id == user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query_history = select(Product_History)
            res_history = await session.execute(query_history)
            result_history = res_history.scalars().all()
            result_list = []

            for history in result_history:
                query_check = select(Warehouse).where(Warehouse.id == history.primary_warehouse)
                res_check = await session.execute(query_check)
                result_check = res_check.scalars().all()
                primary_dict = {}
                if result_check is not None:
                    primary_dict = {
                        'id': res_check[0].id,
                        'name': res_check[0].name,
                        'latitude': res_check[0].latitude,
                        'longitude': res_check[0].longitude
                    }

                query_check = select(Warehouse).where(Warehouse.id == history.next_warehouse)
                res_check = await session.execute(query_check)
                result_check = res_check.scalars().all()
                next_dict = {}
                if result_check is not None:
                    next_dict = {
                        'id': res_check[0].id,
                        'name': res_check[0].name,
                        'latitude': res_check[0].latitude,
                        'longitude': res_check[0].longitude
                    }
                query_product = select(Product).where(Product.id == history.product_id)
                res_product = await session.execute(query_product)
                result_product = res_product.first()
                product_dict = {}
                if result_product is not None:
                    product_dict = {
                        'id': result_product[0].id,
                        'name': result_product[0].name,
                        'price': result_product[0].price,
                        'amount': result_product[0].amount,
                        'category_id': result_product[0].category_id,
                        'joined_at': result_product[0].joined_at
                    }
                result_list.append({
                    'id':history.id,
                'primary_warehouse':primary_dict,
                'next_warehouse':next_dict,
                'product_id':product_dict,
                'count':history.count,
                'carried_at':history.carried_at
                })
            return result_list
