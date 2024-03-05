from datetime import datetime
from typing import List

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, APIRouter, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import load_only

from auth.utills import  generate_token, verify_token
from database import get_async_session

from auth.scheme import UserInfo, UserCreate, User_In_db, UserLogin, Customer_Add, Customer_Get
from models.models import User, Customer

user_register_router = APIRouter()
user_information = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@user_register_router.post('/register', response_model=UserInfo)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_async_session)):
    if user_data.password1 == user_data.password2:
        existing_username = await session.execute(select(User).where(User.username == user_data.username))
        existing_email = await session.execute(select(User).where(User.email == user_data.email))

        if existing_username.scalar_one_or_none():
            raise HTTPException(status_code=400, detail='Username already exists!')
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail='Email already exists!')

        password = pwd_context.hash(user_data.password1)
        user_in_db = User_In_db(**dict(user_data), password=password)
        user_detail = insert(User).values(**dict(user_in_db))
        result = await session.execute(user_detail)
        await session.commit()

        user_info = UserInfo(
            first_name=user_in_db.first_name,
            last_name=user_in_db.last_name,
            username=user_in_db.username,
            email=user_in_db.email,
            phone=user_in_db.phone,
        )
        return dict(user_info)
    else:
        raise HTTPException(status_code=401, detail='Passwords are not same !!!')



@user_register_router.post('/login')
async def login(user: UserLogin, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(User).where(User.username == user.username)
        userdata = await session.execute(query)
        user_data = userdata.one()

        if pwd_context.verify(user.password, user_data[0].password):
            token = generate_token(user_data[0].id)
            return token
        else:
            return {'success': False, 'message': 'Login failed'}
    except:
        return {'success': False, 'message': 'Login failed'}


@user_register_router.get('/user-info', response_model=UserInfo)
async def user_info(token: dict = Depends(verify_token), session: AsyncSession = Depends(get_async_session)):
    if token is None:
        raise HTTPException(status_code=401, detail='Token not provided!')

    user_id = token.get('user_id')

    query = select(User).where(User.id == user_id)
    user = await session.execute(query)
    try:
        result = user.one()
        user_info = UserInfo(
            first_name=result[0].first_name,
            last_name=result[0].last_name,
            username=result[0].username,
            email=result[0].email,
            phone=result[0].phone,
            registration_at=result[0].registration_at
        )
        return user_info
    except NoResultFound:
        raise HTTPException(status_code=404, detail='User not found!')



@user_register_router.post('/customer/add')
async def add_cutomer(model:Customer_Add,
                      token:dict=Depends(verify_token),
                      session : AsyncSession = Depends(get_async_session)
                      ):
    if token is not None:
        existing_email = await session.execute(select(Customer).where(Customer.email == model.email))

        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail='Email already exists!')

        user_id = token.get('user_id')
        query_user = select(User).where(User.id==user_id and User.role_id == 1)
        res = await session.execute(query_user)
        if res.scalar():
            query = insert(Customer).values(**dict(model))
            await session.execute(query)
            await session.commit()
            return {"success":True,"detail":"Customer added!"}


@user_register_router.get('/customer/get',response_model=List[Customer_Get])
async def get_customers(token:dict=Depends(verify_token),
                        session: AsyncSession = Depends(get_async_session)
                        ):
    if token is not None:
        query = select(Customer)
        res = await session.execute(query)
        result = res.scalars().all()
        return result

