from decimal import Decimal
from app.models import Order
from sqlmodel import select

def test_create_order_from_cart(client, auth_headers, mock_cart, mock_cart_item, mock_product):
    response = client.post(
        "/orders/checkout",
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Order successfully submitted."


def test_cart_deleted_after_checkout(client, auth_headers, mock_cart, mock_cart_item):
    client.post("/orders/checkout", headers=auth_headers)

    response = client.get("/cart", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart found."



def test_order_total_is_correct(client, auth_headers, mock_cart, mock_cart_item, mock_product, mock_user, session):
    response = client.post("/orders/checkout", headers=auth_headers)

    assert response.status_code == 201

    order = session.exec(select(Order).where(Order.user_id == mock_user.id)).first()

    expected = mock_product.price * mock_cart_item.quantity

    assert order.total_amount == expected

def test_order_items_snapshot(client, auth_headers, mock_cart, mock_cart_item, mock_product, mock_user, session):
    response = client.post("/orders/checkout", headers=auth_headers)

    assert response.status_code == 201

    order = session.exec(select(Order).where(Order.user_id == mock_user.id)).first()

    item = order.order_items[0]

    assert item.product_id == mock_product.id
    assert item.quantity == mock_cart_item.quantity
    assert item.price_at_purchase == mock_product.price

def test_checkout_empty_cart(client, auth_headers, mock_cart):
    response = client.post("/orders/checkout", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Cart is empty."

def test_checkout_no_cart(client, auth_headers):
    response = client.post("/orders/checkout", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart found."

def test_checkout_product_out_of_stuck(client, auth_headers, mock_cart, mock_cart_item, mock_product, session):
     mock_product.quantity = 0

     session.add(mock_product)
     session.flush()
     session.refresh(mock_product)

     response = client.post("/orders/checkout", headers=auth_headers)

     assert response.status_code == 400
     assert response.json()["detail"] == "Quantity exceeds product stock."
     

def test_get_user_orders(client, auth_headers, mock_cart, mock_cart_item):
    client.post("/orders/checkout", headers=auth_headers)

    response = client.get("/orders", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()["orders"]) == 1

def test_stock_reduced_after_checkout(client, auth_headers, mock_cart, mock_cart_item, mock_product, session):
    old_stock = mock_product.quantity

    client.post("/orders/checkout", headers=auth_headers)

    session.refresh(mock_product)

    assert mock_product.quantity == old_stock - mock_cart_item.quantity

