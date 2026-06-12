from app.schemas import CartItemRead
from app.models import Cart
from decimal import Decimal
from sqlmodel import select
from uuid import UUID, uuid4

def test_read_all_cart_items(client, auth_headers, mock_cart, mock_cart_item, mock_product):
    response = client.get("/cart", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == str(mock_cart_item.id)
    # It is equal to price because there is only one product
    expected_total = mock_cart_item.product.price * mock_cart_item.quantity

    assert Decimal(response.json()["total_amount"]) == expected_total

def test_read_all_cart_items_empty(client, auth_headers, mock_cart):
    response = client.get("/cart", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Cart is empty."

def test_read_all_cart_items_no_cart(client, auth_headers):
    response = client.get("/cart", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart found."

def test_read_cart_authenticated(client):
    response = client.get("/cart")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_read_one_cart_item(client, auth_headers, mock_cart_item):
    response = client.get(f"/cart/{mock_cart_item.id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == str(mock_cart_item.id)

def test_add_one_cart_item_cart_doesnt_exist(client, auth_headers, mock_product, mock_user, session):
    response = client.post("/cart", headers=auth_headers, json={
        "product_id": str(mock_product.id),
        "quantity": 2,
    })

    assert response.status_code == 201
    assert response.json()["product_id"] == str( mock_product.id)
    assert response.json()["quantity"] == 2
    assert response.json()["cart_id"] is not None

    # If no cart exists it should create one
    cart = session.exec(select(Cart).where(Cart.user_id == mock_user.id)).one()

    assert cart.user_id == mock_user.id

def test_add_new_item_to_existing_cart(client, auth_headers, mock_cart, mock_product):
    response = client.post(
        "/cart",
        headers=auth_headers,
        json={
            "product_id": str(mock_product.id),
            "quantity": 2,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["product_id"] == str(mock_product.id)
    assert data["quantity"] == 2

def test_add_one_cart_item_add_quantity(client, auth_headers, mock_product, mock_cart, mock_cart_item):

    old_cart_item_quantity = mock_cart_item.quantity

    response = client.post("/cart", headers=auth_headers, json={
        "product_id": str(mock_product.id),
        "quantity": 2,
    })

    assert response.status_code == 201
    assert response.json()["product_id"] == str(mock_product.id)
    assert response.json()["quantity"] == old_cart_item_quantity + 2

def test_update_cart_item_quantity(client, auth_headers, mock_cart_item):
    response = client.put(
        f"/cart/{mock_cart_item.id}?request_quantity=5",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 5

def test_update_nonexistent_cart_item(client, auth_headers):
    response = client.put(
        f"/cart/{uuid4()}?request_quantity=5",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart item found."

def test_remove_cart_item(client, auth_headers, mock_cart_item):
    response = client.delete(
        f"/cart/{mock_cart_item.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

def test_cart_auto_deletes_when_empty(client, auth_headers, mock_cart_item):
    client.delete(f"/cart/{mock_cart_item.id}", headers=auth_headers)

    response = client.get("/cart", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart found."

def test_add_cart_item_invalid_quantity(client, auth_headers, mock_product):
    response = client.post(
        "/cart",
        headers=auth_headers,
        json={
            "product_id": str(mock_product.id),
            "quantity": 0,
        },
    )

    assert response.status_code == 422

def test_add_nonexistent_product(client, auth_headers):
    response = client.post(
        "/cart",
        headers=auth_headers,
        json={
            "product_id": str(uuid4()),
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No product found."

def test_remove_nonexistent_cart_item(client, auth_headers):
    response = client.delete(f"/cart/{uuid4()}", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart item found."

