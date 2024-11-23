# utils/monday.py
import requests
from django.conf import settings

def add_order_to_monday(order_id, customer_name, order_status, total_price, due_date):
    """
    Add a new order to Monday.com board.

    :param order_id: ID of the order
    :param customer_name: Name of the customer
    :param order_status: Status of the order (e.g., Pending, Completed)
    :param total_price: Total price of the order
    :param due_date: Due date for the order (YYYY-MM-DD format)
    """
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": settings.MONDAY_API_KEY,
        "Content-Type": "application/json"
    }

    query = """
    mutation ($board_id: Int!, $item_name: String!, $column_values: JSON!) {
        create_item (
            board_id: $board_id,
            item_name: $item_name,
            column_values: $column_values
        ) {
            id
        }
    }
    """

    variables = {
        "board_id": int(settings.MONDAY_BOARD_ID),
        "item_name": f"Order #{order_id}",
        "column_values": {
            "status": {"label": order_status},
            "text": customer_name,
            "numbers": total_price,
            "date": {"date": due_date}
        }
    }

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Order added to Monday.com:", data)
        return data
    else:
        print("Failed to add order:", response.text)
        return None
