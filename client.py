import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from pydantic import BaseModel

class ClientItem(BaseModel):
    id: int
    name: str
    address: str
    phone_number: str

class DeletedClientResponse(BaseModel):
    Id: int
    message: str = "Client deleted successfully"

class ClientManager:
    @staticmethod
    def get_all_clients(db_connection):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM client")
                clients = cursor.fetchall()
            return clients
        except psycopg2.Error as e:
            print(f"Error in get_all_clients: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def add_client(db_connection, name: str, address: str, phone_number: str):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "INSERT INTO client (name, address, phone_number) VALUES (%s, %s, %s) RETURNING id",
                    (name, address, phone_number),
                )
                new_client_id = cursor.fetchone()["id"]
            db_connection.commit()

            return ClientItem(ID=new_client_id, name=name, address=address, phone_number=phone_number)
        except psycopg2.Error as e:
            print(f"Error in add_client: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def edit_client(db_connection, client_id: int, name: str, address: str, phone_number: str):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE client SET name = %s, address = %s, phone_number = %s WHERE id = %s",
                    (name, address, phone_number, client_id),
                )
            db_connection.commit()

            return ClientItem(ID=client_id, name=name, address=address, phone_number=phone_number)
        except psycopg2.Error as e:
            print(f"Error in edit_client: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def delete_client(db_connection, client_id: int):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("DELETE FROM client WHERE id = %s RETURNING *", (client_id,))
                deleted_client = cursor.fetchone()
            
            if not deleted_client:
                raise HTTPException(status_code=404, detail="Client not found")

            db_connection.commit()

            return DeletedClientResponse(ID=client_id)
        except psycopg2.Error as e:
            print(f"Error in delete_client: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")