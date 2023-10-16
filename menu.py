import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from pydantic import BaseModel

class MenuItem(BaseModel):
    menu_id: int
    name: str
    price: float

class MessageResponse(BaseModel):
    message: str

class MenuManager:
    @staticmethod
    def get_all_menu_info(db_connection):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM menu")
                menu_items = cursor.fetchall()
            return menu_items
        except Exception as e:
            print(f"Error in get_all_menu_info: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def get_menu_item(db_connection, item_id: int):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM menu WHERE menu_id = %s", (item_id,))
                menu_item = cursor.fetchone()

            if not menu_item:
                raise HTTPException(status_code=404, detail="Item not found")

            return menu_item
        except Exception as e:
            print(f"Error in get_menu_item: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def add_menu_item(db_connection, nombre: str, precio: float):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("INSERT INTO menu (name, price) VALUES (%s, %s) RETURNING menu_id", (nombre, precio))
                new_menu_item_id = cursor.fetchone()[0]
            db_connection.commit()

            return {"message": "Item added successfully", "item_id": new_menu_item_id}
        except Exception as e:
            print(f"Error in add_menu_item: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def update_menu_item(db_connection, item_id: int, nombre: str, precio: float):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("UPDATE menu SET name = %s, price = %s WHERE menu_id = %s", (nombre, precio, item_id))
            db_connection.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item not found")

            return MessageResponse(message="Item updated successfully")
        except Exception as e:
            print(f"Error in update_menu_item: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def delete_menu_item(db_connection, item_id: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM menu WHERE menu_id = %s", (item_id,))
            db_connection.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item not found")

            return MessageResponse(message="Item deleted successfully")
        except Exception as e:
            print(f"Error in delete_menu_item: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
