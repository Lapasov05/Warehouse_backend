from fastapi import FastAPI

from Orders.orders import order_root
from auth.auth import user_register_router
from product.products import product_root
from warehouse.warehouse import warehouse_root

app = FastAPI()




app.include_router(user_register_router,prefix='/auth')
app.include_router(product_root,prefix='/product')
app.include_router(order_root,prefix='/order')
app.include_router(warehouse_root,prefix='/warehouse')