# root_message.pyy

class RootMessage:
    @classmethod
    def get_html_message(cls):
        return """
        <html>
            <head>
                <title>Welcome to Restaurant Chain Restful API</title>
            </head>
            <body>
                <h1>Welcome to Restaurant Chain Restful API</h1>
                <p><b>Documentation:</b> <a href="https://restaurant-chain-api.onrender.com/docs">https://restaurant-chain-api.onrender.com/docs</a></p>
                <p><b>List of all our Endpoints:</b></p>
                <ul>
                    <li>/menu/all_info</li>
                    <li>/menu/{item_id}</li>
                    <li>/menu/add</li>
                    <li>/menu/{item_id}/edit</li>
                    <li>/menu/{item_id}/delete</li>
                    <li>/orders/all_info</li>
                    <li>/orders/{order_id}/details</li>
                    <li>/orders/{order_id}/total_price</li>
                    <li>/orders/add</li>
                    <li>/orders/{order_id}/change_status</li>
                    <li>/orders/{order_id}/add_items</li>
                    <li>/orders/{order_id}/delete</li>
                    <li>/orders/{order_id}/remove_item/{detail_id}</li>
                    <li>/clients/all_info</li>
                    <li>/clients/add</li>
                    <li>/clients/{client_id}/edit</li>
                    <li>/clients/{client_id}/delete</li>
                </ul>
            </body>
        </html>
        """
