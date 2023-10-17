import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from pydantic import BaseModel

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
    def get_all_order_info(db_connection):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM orders")
                orders = cursor.fetchall()
            return orders
        except Exception as e:
            print(f"Error in get_all_order_info: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def get_order_details(db_connection, order_id: int):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM orderdetails WHERE order_id = %s", (order_id,))
                order_details = cursor.fetchall()
            return order_details
        except Exception as e:
            print(f"Error in get_order_details: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def read_order_total_price(db_connection, order_id: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT SUM(menu.price * orderdetails.quantity) AS total_price
                    FROM orders
                    JOIN orderdetails ON orders.order_id = orderdetails.order_id
                    JOIN menu ON orderdetails.item_id = menu.menu_id
                    WHERE orders.order_id = %s
                    """,
                    (order_id,),
                )
                result = cursor.fetchone()
                total_price = result["total_price"] if result["total_price"] is not None else 0
            return {"order_id": order_id, "total_price": total_price}
        except Exception as e:
            print(f"Error in read_order_total_price: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def add_order(db_connection, customer_id: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM client WHERE id = %s", (customer_id,))
                customer_exists = cursor.fetchone()

                if not customer_exists:
                    raise HTTPException(status_code=404, detail="Customer not found")

                cursor.execute("INSERT INTO orders (customer_id, order_status) VALUES (%s, %s) RETURNING order_id", (customer_id, "En cola"))
                new_order_id = cursor.fetchone()[0]
                db_connection.commit()

                return {"result": {"message": "Order added successfully", "order_id": new_order_id}}
        except HTTPException as http_error:
            # Re-raise HTTPException to be handled by FastAPI
            raise http_error
        except Exception as e:
            print(f"Error in add_order: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def change_order_status(db_connection, order_id: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT order_status FROM orders WHERE order_id = %s", (order_id,))
                current_status = cursor.fetchone()

                if not current_status:
                    raise HTTPException(status_code=404, detail="Order not found")

                if current_status["order_status"] == "En cola":
                    new_status = "En proceso"
                elif current_status["order_status"] == "En proceso":
                    new_status = "Entregado"
                else:
                    return {"result": {"message": "Order has already been delivered"}}

                cursor.execute("UPDATE orders SET order_status = %s WHERE order_id = %s", (new_status, order_id))
            db_connection.commit()

            return {"result": {"message": "Order status changed successfully"}}
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def add_items_to_order(db_connection, order_id: int, item_id: int, quantity: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM menu WHERE menu_id = %s", (item_id,))
                menu_item = cursor.fetchone()

                if not menu_item:
                    raise HTTPException(status_code=404, detail="Menu item not found")

                cursor.execute("INSERT INTO orderdetails (order_id, item_id, quantity) VALUES (%s, %s, %s)", (order_id, item_id, quantity))
            db_connection.commit()

            return {"result": {"message": "Items added to order successfully"}}
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def delete_order(db_connection, order_id: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT order_status FROM orders WHERE order_id = %s", (order_id,))
                order_status_result = cursor.fetchone()

                if not order_status_result:
                    raise HTTPException(status_code=404, detail="Order not found")

                order_status = order_status_result[0]  # Accessing the first (and only) element in the tuple

                if order_status not in ["En cola", "En proceso"]:
                    raise HTTPException(status_code=400, detail="Cannot delete order in the current state")

                cursor.execute("DELETE FROM orderdetails WHERE order_id = %s", (order_id,))
                cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
            db_connection.commit()

            return {"result": {"message": "Order and details deleted successfully"}}
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


    @staticmethod
    def remove_item_from_order(db_connection, order_id: int, detail_id: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM orderdetails WHERE order_id = %s AND detail_id = %s", (order_id, detail_id))
            db_connection.commit()

            return {"result": {"message": "Item removed from order successfully"}}
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
