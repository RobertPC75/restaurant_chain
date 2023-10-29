import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor
from typing import List
from fastapi.responses import JSONResponse, HTMLResponse
from menu import MenuManager, MenuItem, MessageResponse
from orders import OrderManager, OrderInfo, OrderItem
from client import ClientManager, ClientItem, DeletedClientResponse
from root_message import RootMessage

app = FastAPI()

# Datos de conexión a la base de datoss
DATABASE_URL = "postgres://restaurant_chain_db_user:BbXEd4RhkuzaQt7K2dmW38LIZ8mOF34y@dpg-ckm6i4iv7m0s73fkuo20-a/restaurant_chain_db"

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000", 
    "http://localhost:3000",
    "https://restaurant-chain-fe2.onrender.com",  # Add Render URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    message = RootMessage.get_html_message()
    return HTMLResponse(content=message)

@app.get("/menu/all_info", response_model=List[MenuItem])
def read_all_menu_info():
    with get_db_connection() as conn:
        return MenuManager.get_all_menu_info(conn)

@app.get("/menu/{item_id}", response_model=MenuItem)
def read_menu_item(item_id: int):
    with get_db_connection() as conn:
        return MenuManager.get_menu_item(conn, item_id)

@app.post("/menu/add", response_model=MessageResponse)
def add_menu_item(nombre: str, precio: float):
    with get_db_connection() as conn:
        return MenuManager.add_menu_item(conn, nombre, precio)

@app.put("/menu/{item_id}/edit", response_model=MessageResponse)
def update_menu_item(item_id: int, nombre: str, precio: float):
    with get_db_connection() as conn:
        return MenuManager.update_menu_item(conn, item_id, nombre, precio)

@app.delete("/menu/{item_id}/delete", response_model=MessageResponse)
def delete_menu_item(item_id: int):
    with get_db_connection() as conn:
        return MenuManager.delete_menu_item(conn, item_id)
    
order_manager = OrderManager()

@app.get("/orders/all_info", response_model=List[OrderInfo])
def read_all_order_info():
    with get_db_connection() as conn:
        return order_manager.get_all_order_info(conn)

@app.get("/orders/{order_id}/details", response_model=List[OrderItem])
def read_order_details(order_id: int):
    with get_db_connection() as conn:
        return order_manager.get_order_details(conn, order_id)

@app.get("/orders/{order_id}/total_price")
def read_order_total_price(order_id: int):
    with get_db_connection() as conn:
        return order_manager.read_order_total_price(conn, order_id)

@app.post("/orders/add")
def add_order(customer_id: int):
    with get_db_connection() as conn:
        return order_manager.add_order(conn, customer_id)

@app.put("/orders/{order_id}/change_status")
def change_order_status(order_id: int):
    with get_db_connection() as conn:
        return order_manager.change_order_status(conn, order_id)

@app.post("/orders/{order_id}/add_items")
def add_items_to_order(order_id: int, item_id: int, quantity: int):
    with get_db_connection() as conn:
        return order_manager.add_items_to_order(conn, order_id, item_id, quantity)

@app.delete("/orders/{order_id}/delete")
def delete_order(order_id: int):
    with get_db_connection() as conn:
        return order_manager.delete_order(conn, order_id)

@app.delete("/orders/{order_id}/remove_item/{detail_id}")
def remove_item_from_order(order_id: int, detail_id: int):
    with get_db_connection() as conn:
        return order_manager.remove_item_from_order(conn, order_id, detail_id)

client_manager = ClientManager()

@app.get("/clients/all_info", response_model=List[ClientItem])
def get_all_clients():
    with get_db_connection() as conn:
        return client_manager.get_all_clients(conn)

@app.post("/clients/add", response_model=ClientItem)
def add_client(name: str, address: str, phone_number: str):
    with get_db_connection() as conn:
        return client_manager.add_client(conn, name, address, phone_number)

@app.put("/clients/{client_id}/edit", response_model=ClientItem)
def edit_client(client_id: int, name: str, address: str, phone_number: str):
    with get_db_connection() as conn:
        return client_manager.edit_client(conn, client_id, name, address, phone_number)

@app.delete("/clients/{client_id}/delete", response_model=DeletedClientResponse)
def delete_client(client_id: int):
    with get_db_connection() as conn:
        return client_manager.delete_client(conn, client_id)

