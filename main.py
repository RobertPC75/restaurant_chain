from fastapi import FastAPI, HTTPException
from mysql.connector import connect, Error
from typing import List
from menu import Menu, MenuItem
from orders import OrderManager, OrderInfo, OrderItem
from client import Client

app = FastAPI()

# Configuración de la conexión a la base de datos
db_config = {
    'host': '127.0.0.1',  
    'user': 'root',     
    'password': 'Law61972961!',  
    'database': 'restaurant_chain'  
}

@app.get("/menu/all_info")
def read_all_menu_info():
    return Menu.get_all_menu_info(db_config)

@app.get("/menu/{item_id}")
def read_menu_item(item_id: int):
    return Menu.get_menu_item(db_config, item_id)

@app.post("/menu")
def add_menu_item(nombre: str, precio: float):
    return Menu.add_menu_item(db_config, nombre, precio)

@app.put("/menu/{item_id}")
def update_menu_item(item_id: int, nombre: str, precio: float):
    return Menu.update_menu_item(db_config, item_id, nombre, precio)

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int):
    return Menu.delete_menu_item(db_config, item_id)

order_manager = OrderManager()

@app.get("/orders/all_info", response_model=List[OrderInfo])
def read_all_order_info():
    return order_manager.get_all_order_info(db_config)

@app.get("/orders/{order_id}/details", response_model=List[OrderItem])
def read_order_details(order_id: int):
    return order_manager.get_order_details(db_config, order_id)

@app.get("/orders/{order_id}/total_price")
def read_order_total_price(order_id: int):
    return order_manager.read_order_total_price(db_config, order_id)

@app.post("/orders/add")
def add_order(customer_id: int):
    return order_manager.add_order(db_config, customer_id)

@app.put("/orders/{order_id}/change_status")
def change_order_status(order_id: int):
    return order_manager.change_order_status(db_config, order_id)

@app.post("/orders/{order_id}/add_items")
def add_items_to_order(order_id: int, item_id: int, quantity: int):
    return order_manager.add_items_to_order(db_config, order_id, item_id, quantity)

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    return order_manager.delete_order(db_config, order_id)

@app.delete("/orders/{order_id}/remove_item/{detail_id}")
def remove_item_from_order(order_id: int, detail_id: int):
    return order_manager.remove_item_from_order(db_config, order_id, detail_id)

# Obtener todos los clientes
@app.get("/clients", response_model=List[Client])
def get_all_clients():
    return Client.get_all_clients(db_config)

# Agregar nuevo cliente
@app.post("/clients", response_model=Client)
def add_client(name: str, address: str, phone_number: str):
    return Client.add_client(db_config, name, address, phone_number)

# Editar cliente
@app.put("/clients/{client_id}", response_model=Client)
def edit_client(client_id: int, name: str, address: str, phone_number: str):
    return Client.edit_client(db_config, client_id, name, address, phone_number)

# Eliminar cliente
@app.delete("/clients/{client_id}", response_model=Client)
def delete_client(client_id: int):
    return Client.delete_client(db_config, client_id)