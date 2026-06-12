# Fix app import problem
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.core.security import password_hash
from app.main import app
from app.dependency import get_session
from app.models import *


test_engine = create_engine(
    settings.SQLITE_TEST_URL,
    connect_args={"check_same_thread": False}
)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture
def session():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# Override dependency
def override_get_session(session):
    def _override():
        yield session
    return _override

# app.dependency_overrides[get_session] = override_get_session

@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = override_get_session(session)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
def mock_user(session: Session):
    user = User(
        email="test@example.com",
        full_name="test mcTesty",
        hashed_password=password_hash.hash("test_password")
    )

    session.add(user)
    session.flush()
    session.refresh(user)
    return user

@pytest.fixture
def mock_admin_user(session: Session):
    user = User(
        email=settings.INITIAL_SUPERUSER,
        full_name="admin istator",
        hashed_password=password_hash.hash(settings.INITIAL_SUPERUSER_PASSWORD),
        is_superuser=True
    )

    session.add(user)
    session.flush()
    session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, mock_user):
    response = client.post(
        "/auth/token",
        data={
            "username": mock_user.email,
            "password": "test_password",
        },
    )
    return {
        "Authorization": f"Bearer {response.json()["access_token"]}"
    }

@pytest.fixture
def admin_auth_headers(client, mock_admin_user):
    response = client.post(
        "/auth/token",
        data={
            "username": settings.INITIAL_SUPERUSER,
            "password": settings.INITIAL_SUPERUSER_PASSWORD,
        },
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_product(session: Session):
    product = Product(
        title="Test Product",
        description="This is a test product",
        price=100,
        quantity=10
    )

    session.add(product)
    session.flush()
    session.refresh(product)
    return product

@pytest.fixture
def mock_cart(session, mock_user):
    cart = Cart(user_id=mock_user.id)

    session.add(cart)
    session.flush()
    session.refresh(cart)

    return cart

@pytest.fixture
def mock_cart_item(session, mock_cart, mock_product):
    cart_item = CartItem(
        cart_id=mock_cart.id,
        product_id=mock_product.id,
        quantity=2,
    )

    session.add(cart_item)
    session.flush()
    session.refresh(cart_item)

    return cart_item

