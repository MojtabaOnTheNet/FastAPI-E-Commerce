from sqlmodel import select
from uuid import UUID, uuid4
from app.models import Product, Cart, Order, User

def test_admin_create_product(client, admin_auth_headers):
    response = client.post("/admin/products", headers=admin_auth_headers, json={
        "title": "test_admin Product",
        "description": "This is a test_admin product",
        "price": 100,
        "quantity": 10
    })

    assert response.status_code == 201
    assert response.json()["title"] == "test_admin Product"
    assert response.json()["price"] == "100.00"
    assert response.json()["quantity"] == 10
    assert "id" in response.json()

def test_admin_update_product(client, admin_auth_headers, mock_product, session):
    response = client.put(f"/admin/products/{mock_product.id}", headers=admin_auth_headers, json={
        "title": "test_admin Product Updated",
    })

    assert response.status_code == 204

    session.refresh(mock_product)

    assert mock_product.title == "test_admin Product Updated"

def test_admin_delete_product(client, admin_auth_headers, mock_product, session):
    response = client.delete(f"/admin/products/{mock_product.id}", headers=admin_auth_headers)

    assert response.status_code == 204

    product = session.exec(
        select(Product).where(Product.id == mock_product.id)
    ).first()

    assert product is None

def test_admin_read_any_cart(client, admin_auth_headers, mock_product, mock_cart, mock_cart_item, mock_user):
    response = client.get(f"/admin/carts/{mock_user.id}", headers=admin_auth_headers)

    assert response.status_code == 200
    assert response.json()["user_id"] == str(mock_user.id)

def test_admin_delete_any_cart(client, admin_auth_headers, mock_product, mock_cart, mock_cart_item, mock_user, session):
    response = client.delete(f"/admin/carts/{mock_user.id}", headers=admin_auth_headers)

    cart = session.exec(
        select(Cart).where(Cart.id == mock_cart.id)
    ).first()

    assert response.status_code == 204
    assert cart is None

def test_admin_read_all_orders(client, admin_auth_headers, auth_headers, mock_cart, mock_cart_item, mock_product, mock_user):
    # create order with the normal user
    client.post(
        "/orders/checkout",
        headers=auth_headers,
    )

    response = client.get("/admin/orders/", headers=admin_auth_headers)

    assert response.status_code == 200 
    assert len(response.json()["orders"]) >= 1
    assert response.json()["orders"][0]["user_id"] == str(mock_user.id)

def test_admin_change_order_status(client, admin_auth_headers, auth_headers, mock_cart, mock_cart_item, mock_product, mock_user, session):
    # create order with the normal user
    client.post(
        "/orders/checkout",
        headers=auth_headers,
    )

    order = session.exec(select(Order).where(Order.user_id == mock_user.id)).first()

    response = client.put(f"/admin/orders/{order.id}", headers=admin_auth_headers, json={
        "status": "fulfilled"
    })

    assert response.status_code == 204

    session.refresh(order)

    assert order.status == "fulfilled"

def test_admin_read_all_users(client, admin_auth_headers, mock_user):
    response = client.get("/admin/users", headers=admin_auth_headers)

    assert response.status_code == 200

    # Two Users because it includes the admin
    assert len(response.json()["users"]) >= 1

    user_ids = [user["id"] for user in response.json()["users"]]


    assert str(mock_user.id) in user_ids

def test_admin_update_user_privileges(client, admin_auth_headers, mock_user, session):
    response = client.put(f"/admin/users/{mock_user.id}", headers=admin_auth_headers, json={
        "is_active": False
    })

    user = session.exec(select(User).where(User.id == mock_user.id)).first()

    assert response.status_code == 204
    assert user.is_active == False

def test_admin_delete_user(client, admin_auth_headers, mock_user, session):
    response = client.delete(f"/admin/users/{mock_user.id}", headers=admin_auth_headers)

    assert response.status_code == 204

    user = session.exec(select(User).where(User.id == mock_user.id)).first()

    assert user is None


def test_admin_user_cannot_create_product(client, auth_headers):
    response = client.post(
        "/admin/products",
        headers=auth_headers,
        json={
            "title": "Hack Product",
            "price": 100,
            "quantity": 1,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges."

def test_admin_create_product_invalid_price(client, admin_auth_headers):
    response = client.post(
        "/admin/products",
        headers=admin_auth_headers,
        json={
            "title": "Bad Product",
            "price": "free",
            "quantity": 10,
        },
    )

    assert response.status_code == 422


def test_admin_update_nonexistent_product(client, admin_auth_headers):
    response = client.put(
        f"/admin/products/{uuid4()}",
        headers=admin_auth_headers,
        json={"title": "New"},
    )

    # it is not 404 because of the request model
    assert response.status_code == 422

def test_admin_delete_nonexistent_product(client, admin_auth_headers):
    response = client.delete(
        f"/admin/products/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No product found."

def test_admin_user_cannot_access_admin_users(client, auth_headers):
    response = client.get("/admin/users", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges."

def test_admin_unauthenticated_user_cannot_access_admin_users(client):
    response = client.get("/admin/users")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_admin_update_user_invalid_payload(client, admin_auth_headers, mock_user):
    response = client.put(
        f"/admin/users/{mock_user.id}",
        headers=admin_auth_headers,
        json={"is_active": "not_a_boolean"},
    )

    assert response.status_code == 422

def test_admin_user_cannot_access_admin_cart(client, auth_headers, mock_user):
    response = client.get(
        f"/admin/carts/{mock_user.id}",
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges."

def test_admin_get_nonexistent_user_cart(client, admin_auth_headers):
    response = client.get(
        f"/admin/carts/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart found."

def test_admin_delete_nonexistent_cart(client, admin_auth_headers):
    response = client.delete(
        f"/admin/carts/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No cart found."

def test_admin_user_cannot_access_admin_orders(client, auth_headers):
    response = client.get("/admin/orders/", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges."

def test_admin_update_order_invalid_status(client, admin_auth_headers, auth_headers, mock_cart, mock_cart_item, mock_product, mock_user, session):
    # create order with the normal user
    client.post(
        "/orders/checkout",
        headers=auth_headers,
    )

    order = session.exec(select(Order).where(Order.user_id == mock_user.id)).first()


    response = client.put(
        f"/admin/orders/{order.id}",
        headers=admin_auth_headers,
        json={"status": 123},
    )

    assert response.status_code == 422

def test_admin_user_cannot_update_order_status(client, admin_auth_headers, auth_headers, mock_cart, mock_cart_item, mock_product, mock_user, session):
    # create order with the normal user
    client.post(
        "/orders/checkout",
        headers=auth_headers,
    )

    order = session.exec(select(Order).where(Order.user_id == mock_user.id)).first()


    response = client.put(
        f"/admin/orders/{order.id}",
        headers=auth_headers,
        json={"status": "fulfilled"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges."


# Global test_admin for SECURITY

ENDPOINTS = [
    "/admin/users",
    "/admin/orders",
]

def test_admin_routes_require_auth(client):
    for endpoint in ENDPOINTS:
        response = client.get(endpoint)

        assert response.status_code == 401

def test_admin_routes_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/admin/users", headers=headers)

    assert response.status_code in (401, 403)

