from fastapi import HTTPException
from mysql.connector import connect, Error
from pydantic import BaseModel
from typing import Dict, List

class OrderItem(BaseModel):
    detail_id: int
    order_id: int
    item_id: int
    quantity: int

class OrderInfo(BaseModel):
    order_id: int
    customer_id: int
    order_status: str

class OrderManager:
    @staticmethod
    def get_all_order_info(db_config) -> List[OrderInfo]:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT order_id, customer_id, order_status FROM Orders"
                    cursor.execute(query)
                    result = cursor.fetchall()

                    # Ensure that customer_id is not None
                    order_info = [
                        OrderInfo(
                            order_id=item[0],
                            customer_id=item[1] if item[1] is not None else 0,  # Provide a default value (e.g., 0)
                            order_status=item[2]
                        ) for item in result
                    ]
                    return order_info

        except Error as e:
            print(f"Error in get_all_order_info: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    @staticmethod
    def get_order_details(db_config, order_id: int) -> List[OrderItem]:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM OrderDetails WHERE order_id = %s"
                    cursor.execute(query, (order_id,))
                    result = cursor.fetchall()

                    order_details = [
                        OrderItem(
                            detail_id=item[0],
                            order_id=item[1],
                            item_id=item[2],
                            quantity=item[3]
                        ) for item in result
                    ]
                    return order_details

        except Error as e:
            print(f"Error in get_order_details: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    @staticmethod
    def read_order_total_price(db_config, order_id: int):
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = """
                        SELECT SUM(Menu.price * OrderDetails.quantity) 
                        FROM OrderDetails 
                        JOIN Menu ON OrderDetails.item_id = Menu.menu_id 
                        WHERE OrderDetails.order_id = %s
                    """
                    cursor.execute(query, (order_id,))
                    total_price = cursor.fetchone()[0]
                    return {"order_id": order_id, "total_price": total_price}

        except Error as e:
            print(f"Error in read_order_total_price: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


    @staticmethod
    def add_order(db_config, customer_id: int):
        try:
            # Verificar si el cliente existe
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    check_customer_query = "SELECT 1 FROM client WHERE id = %s"
                    cursor.execute(check_customer_query, (customer_id,))
                    customer_exists = cursor.fetchone()

                    if not customer_exists:
                        raise HTTPException(status_code=404, detail="Customer not found")

                    # Continuar con la inserción de la orden
                    insert_order_query = "INSERT INTO Orders (customer_id, order_status) VALUES (%s, %s)"
                    cursor.execute(insert_order_query, (customer_id, "En cola"))
                    connection.commit()

                    return {"message": "Order added successfully", "order_id": cursor.lastrowid}

        except Error as e:
            print(f"Error in add_order: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def change_order_status(db_config, order_id: int):
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    get_status_query = "SELECT order_status FROM Orders WHERE order_id = %s"
                    cursor.execute(get_status_query, (order_id,))
                    current_status = cursor.fetchone()

                    if not current_status:
                        raise HTTPException(status_code=404, detail="Order not found")

                    current_status = current_status[0]

                    if current_status == "En cola":
                        new_status = "En proceso"
                    elif current_status == "En proceso":
                        new_status = "Entregado"
                    else:
                        return {"message": "Order has already been delivered"}

                    update_status_query = "UPDATE Orders SET order_status = %s WHERE order_id = %s"
                    cursor.execute(update_status_query, (new_status, order_id))
                    connection.commit()

                    return {"message": "Order status changed successfully"}

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def add_items_to_order(db_config, order_id: int, item_id: int, quantity: int):
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    menu_query = "SELECT * FROM Menu WHERE menu_id = %s"
                    cursor.execute(menu_query, (item_id,))
                    menu_item = cursor.fetchone()

                    if not menu_item:
                        raise HTTPException(status_code=404, detail="Menu item not found")

                    order_details_query = "INSERT INTO OrderDetails (order_id, item_id, quantity) VALUES (%s, %s, %s)"
                    cursor.execute(order_details_query, (order_id, item_id, quantity))
                    connection.commit()

                    return {"message": "Items added to order successfully"}

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def delete_order(db_config, order_id: int):
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    check_order_query = "SELECT order_status FROM Orders WHERE order_id = %s"
                    cursor.execute(check_order_query, (order_id,))
                    order_status = cursor.fetchone()

                    if not order_status:
                        raise HTTPException(status_code=404, detail="Order not found")

                    order_status = order_status[0]

                    if order_status not in ["En cola", "En proceso"]:
                        raise HTTPException(status_code=400, detail="Cannot delete order in current state")

                    delete_order_details_query = "DELETE FROM OrderDetails WHERE order_id = %s"
                    cursor.execute(delete_order_details_query, (order_id,))

                    delete_order_query = "DELETE FROM Orders WHERE order_id = %s"
                    cursor.execute(delete_order_query, (order_id,))

                    connection.commit()

                    return {"message": "Order and details deleted successfully"}

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def remove_item_from_order(db_config, order_id: int, detail_id: int):
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    check_detail_query = "SELECT * FROM OrderDetails WHERE detail_id = %s AND order_id = %s"
                    cursor.execute(check_detail_query, (detail_id, order_id))
                    order_detail = cursor.fetchone()

                    if not order_detail:
                        raise HTTPException(status_code=404, detail="Order detail not found")

                    delete_detail_query = "DELETE FROM OrderDetails WHERE detail_id = %s"
                    cursor.execute(delete_detail_query, (detail_id,))
                    connection.commit()

                    return {"message": "Item removed from order successfully"}

        except Error as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
