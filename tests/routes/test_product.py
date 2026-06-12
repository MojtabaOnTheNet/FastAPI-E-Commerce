import uuid

def test_read_all_products(client, mock_product):
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["data"][0]["id"] == str(mock_product.id)
    

def test_read_all_products_none(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json()["count"] == 0
    assert response.json()["data"] == []

def test_read_product(client, mock_product):
    response = client.get(f"/products/{mock_product.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(mock_product.id)
    assert response.json()["title"] == mock_product.title

def test_read_product_none(client):
    response = client.get(f"/products/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "No product found."

def test_read_product_invalid_uuid(client):
    response = client.get("/products/not_a_uuid")

    assert response.status_code == 422
