from fastapi import HTTPException
from mysql.connector import connect, Error
from pydantic import BaseModel
from typing import List


class MenuItem(BaseModel):
    menu_id: int
    name: str
    price: float

class Menu:
    @staticmethod
    def get_all_menu_info(db_config) -> List[MenuItem]:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT menu_id, name, price FROM Menu"
                    cursor.execute(query)
                    result = cursor.fetchall()
                    menu_info = [MenuItem(menu_id=item[0], name=item[1], price=item[2]) for item in result]
                    return menu_info

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def get_menu_item(db_config, item_id: int) -> MenuItem:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM Menu WHERE menu_id = %s"
                    cursor.execute(query, (item_id,))
                    result = cursor.fetchone()

                    if result is None:
                        raise HTTPException(status_code=404, detail="Item not found")

                    return MenuItem(menu_id=result[0], name=result[1], price=result[2])

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def add_menu_item(db_config, nombre: str, precio: float) -> dict:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "INSERT INTO Menu (name, price) VALUES (%s, %s)"
                    cursor.execute(query, (nombre, precio))
                    connection.commit()
                    return {"message": "Item added successfully", "item_id": cursor.lastrowid}

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def update_menu_item(db_config, item_id: int, nombre: str, precio: float) -> dict:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "UPDATE Menu SET name = %s, price = %s WHERE menu_id = %s"
                    cursor.execute(query, (nombre, precio, item_id))
                    connection.commit()

                    if cursor.rowcount == 0:
                        raise HTTPException(status_code=404, detail="Item not found")

                    return {"message": "Item updated successfully", "item_id": item_id}

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def delete_menu_item(db_config, item_id: int) -> dict:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "DELETE FROM Menu WHERE menu_id = %s"
                    cursor.execute(query, (item_id,))
                    connection.commit()

                    if cursor.rowcount == 0:
                        raise HTTPException(status_code=404, detail="Item not found")

                    return {"message": "Item deleted successfully"}
                    
        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
