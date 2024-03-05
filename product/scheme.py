from datetime import date, datetime

from pydantic import BaseModel


class Add_Product(BaseModel):
    name:str
    price:float
    amount:int
    category_id:int
    warehouse_id:int


class Get_Products(BaseModel):
    id:int
    name:str
    price:float
    amount:int
    category_id:int
    warehouse_id:int
    joined_at:datetime


class Get_categories(BaseModel):
    id:int
    name : str