import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional

class ClientItem(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    clerkid: Optional[str] = None

class DeletedClientResponse(BaseModel):
    id: int
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
    def add_client(
        db_connection, name: str, 
        address: Optional[str] = None, phone_number: Optional[str] = None, clerkid: Optional[str] = None
    ):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "INSERT INTO client (name, address, phone_number, clerkid) VALUES (%s, %s, %s, %s) RETURNING id",
                    (name, address, phone_number, clerkid),
                )
                new_client_id = cursor.fetchone()["id"]
            db_connection.commit()

            return ClientItem(id=new_client_id, name=name, address=address, phone_number=phone_number, clerkid=clerkid)
        except psycopg2.Error as e:
            print(f"Error in add_client: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def edit_client(
        db_connection, client_id: int, name: str, 
        address: Optional[str] = None, phone_number: Optional[str] = None
    ):
        try:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE client SET name = %s, address = %s, phone_number = %s WHERE id = %s",
                    (name, address, phone_number, client_id),
                )
            db_connection.commit()

            return ClientItem(id=client_id, name=name, address=address, phone_number=phone_number)
        except psycopg2.Error as e:
            print(f"Error in edit_client: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def delete_client(db_connection, client_id: int):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("DELETE FROM client WHERE id = %s RETURNING id", (client_id,))
                deleted_client = cursor.fetchone()

            if not deleted_client:
                raise HTTPException(status_code=404, detail="Client not found")

            db_connection.commit()

            return DeletedClientResponse(id=client_id)
        except psycopg2.Error as e:
            print(f"Error in delete_client: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def get_client_details(db_connection, client_id: int):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, name, address, phone_number FROM client WHERE id = %s", (client_id,))
                client_details = cursor.fetchone()

            if not client_details:
                raise HTTPException(status_code=404, detail="Client not found")

            return ClientItem(**client_details)
        except psycopg2.Error as e:
            print(f"Error in get_client_details: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    @staticmethod
    def get_client_details_by_clerk_id(db_connection, clerk_id: str):
        try:
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, name, address, phone_number, clerkid FROM client WHERE clerkid = %s", (clerk_id,))
                client_details = cursor.fetchone()

            if not client_details:
                raise HTTPException(status_code=404, detail="Client not found")

            return ClientItem(**client_details)
        except psycopg2.Error as e:
            print(f"Error in get_client_details_by_clerk_id: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


