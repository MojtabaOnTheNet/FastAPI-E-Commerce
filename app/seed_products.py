from decimal import Decimal
from faker import Faker
from sqlmodel import Session

import random

from models import Product
from database import engine

fake = Faker()

BRANDS = [
    "Apple",
    "Samsung",
    "Sony",
    "Dell",
    "HP",
    "Lenovo",
    "Asus",
    "LG",
    "Logitech",
    "Razer",
    "Corsair",
    "Anker",
    "Microsoft",
    "Acer",
]

PRODUCT_TYPES = {
    "Laptop": ["Pro", "Air", "Ultra", "Elite"],
    "Monitor": ["4K", "UltraWide", "Gaming", "Professional"],
    "Keyboard": ["Mechanical", "Wireless", "Gaming"],
    "Mouse": ["Wireless", "Gaming", "Ergonomic"],
    "Headphones": ["Studio", "Wireless", "Noise Cancelling"],
    "Speaker": ["Bluetooth", "Portable", "Smart"],
    "SSD": ["NVMe", "Portable", "External"],
    "Webcam": ["HD", "Full HD", "4K"],
    "Docking Station": ["USB-C", "Thunderbolt", "Universal"],
    "Smart Watch": ["Sport", "Pro", "Premium"],
}


def generate_product() -> Product:
    product_type = random.choice(list(PRODUCT_TYPES.keys()))
    variant = random.choice(PRODUCT_TYPES[product_type])
    brand = random.choice(BRANDS)

    title = (
        f"{brand} "
        f"{product_type} "
        f"{variant} "
        f"{random.randint(1000, 9999)}"
    )

    description = fake.text(max_nb_chars=180)

    return Product(
        title=title,
        description=description,
        price=Decimal(f"{random.uniform(9.99, 4999.99):.2f}"),
        quantity=random.randint(0, 1000),
    )


def seed_products(count: int = 1000) -> None:
    with Session(engine) as session:
        products = [generate_product() for _ in range(count)]

        session.add_all(products)
        session.commit()

    print(f"Inserted {count:,} products")


if __name__ == "__main__":
    seed_products(10000)