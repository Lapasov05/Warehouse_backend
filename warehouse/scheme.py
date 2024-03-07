from datetime import datetime

from pydantic import BaseModel

from product.scheme import Get_Products


class Add_warehouse(BaseModel):
    name : str
    long : float
    lat: float


class Get_warehouse(BaseModel):
    id:int
    name : str
    long : float
    lat: float


class Get_warehouse(BaseModel):
    id:int
    name:str
    latitude:float
    longitude:float

class Product_history(BaseModel):
    id:int
    primary_warehouse:Get_warehouse
    next_warehouse:Get_warehouse
    product_id:Get_Products
    carried_at:datetime
