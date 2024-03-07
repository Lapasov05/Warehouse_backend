from datetime import datetime

from pydantic import BaseModel

from auth.scheme import Customer_Get, UserInfo
from product.scheme import Get_Products
from warehouse.scheme import Get_warehouse


class Get_orders(BaseModel):
    id:int
    customer_id:Customer_Get
    created_at:datetime
    user_id:UserInfo
    is_active:bool

class Get_orders_shoppping(BaseModel):
    id:int
    customer_id:int
    created_at:datetime
    user_id:int
    is_active:bool


class Get_shopping_carts(BaseModel):
    id:int
    order_id:Get_orders_shoppping
    product_id:Get_Products
    amount:int
    total:float
    is_active:bool

class Get_history(BaseModel):
    id : int
    primary_warehouse:Get_warehouse
    next_warehouse:Get_warehouse
    product_id:Get_Products
    count : int
    carried_at:datetime