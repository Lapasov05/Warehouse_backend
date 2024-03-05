from datetime import datetime

from pydantic import BaseModel


class Get_orders(BaseModel):
    id:int
    customer_id:int
    created_at:datetime
    user_id:int
    is_active:bool


class Get_shopping_carts(BaseModel):
    id:int
    order_id:int
    product_id:int
    amount:int
    total:float
    is_active:bool