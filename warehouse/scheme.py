from datetime import datetime

from pydantic import BaseModel


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
    warehouse_id:int
    category_id:int