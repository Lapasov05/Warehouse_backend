from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    first_name:str
    last_name:str
    username:str
    email:str
    phone:str
    password1:str
    password2:str



class User_In_db(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    phone: str



class UserInfo(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    phone: str


class UserLogin(BaseModel):
    username: str
    password: str


class Customer_Add(BaseModel):
    first_name : str
    last_name : str
    phone : str
    email : str


class Customer_Get(BaseModel):
    id:int
    first_name : str
    last_name : str
    phone : str
    email : str
