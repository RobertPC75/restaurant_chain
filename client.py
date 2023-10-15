from pydantic import BaseModel
from typing import List
from mysql.connector import connect, Error

class Client(BaseModel):
    ID: int
    name: str
    address: str
    phone_number: str

    @staticmethod
    def get_all_clients(db_config) -> List['Client']:
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "SELECT ID, name, address, phone_number FROM client"
                    cursor.execute(query)
                    result = cursor.fetchall()

                    clients = [Client(ID=item[0], name=item[1], address=item[2], phone_number=item[3]) for item in result]
                    return clients

        except Error as e:
            print(f"Error in get_all_clients: {e}")
            raise

    @staticmethod
    def add_client(db_config, name: str, address: str, phone_number: str) -> 'Client':
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "INSERT INTO client (name, address, phone_number) VALUES (%s, %s, %s)"
                    cursor.execute(query, (name, address, phone_number))
                    connection.commit()
                    client_id = cursor.lastrowid

                    return Client(ID=client_id, name=name, address=address, phone_number=phone_number)

        except Error as e:
            print(f"Error in add_client: {e}")
            raise

    @staticmethod
    def edit_client(db_config, client_id: int, name: str, address: str, phone_number: str) -> 'Client':
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "UPDATE client SET name = %s, address = %s, phone_number = %s WHERE ID = %s"
                    cursor.execute(query, (name, address, phone_number, client_id))
                    connection.commit()

                    return Client(ID=client_id, name=name, address=address, phone_number=phone_number)

        except Error as e:
            print(f"Error in edit_client: {e}")
            raise

    @staticmethod
    def delete_client(db_config, client_id: int) -> 'Client':
        try:
            with connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    query = "DELETE FROM client WHERE ID = %s"
                    cursor.execute(query, (client_id,))
                    connection.commit()

                    return Client(ID=client_id, name="", address="", phone_number="")

        except Error as e:
            print(f"Error in delete_client: {e}")
            raise
