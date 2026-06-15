# 🛒 FastAPI E-Commerce Backend

A modern, scalable **E-Commerce backend API** built with **FastAPI**, designed for learning, portfolio showcase, and real-world backend architecture practice.

It includes core e-commerce features like **authentication, product management, shopping carts, and order processing**, built with clean architecture principles using SQLModel and relational databases.

---

## 🚀 Features

- 👤 JWT-based authentication and authorization
- 🔐 Password hashing and secure credential handling
- 🛍️ Product management (CRUD operations)
- 🛒 Shopping cart functionality
- 📦 Order creation and checkout workflow
- 👑 Admin-only endpoints for management operations
- 🧾 SQLModel relationships and data validation
- ⚡ FastAPI-powered REST API
- 📖 Automatic API documentation with Swagger UI and ReDoc
- 🗄️ Database migrations with Alembic
- 🧩 Modular and scalable project structure

---

## 🏗️ Tech Stack

| Technology | Purpose             |
| ---------- | ------------------- |
| FastAPI    | Web framework       |
| SQLModel   | ORM and data models |
| SQLAlchemy | Database engine     |
| SQLite     | Database            |
| Pydantic   | Data validation     |
| JWT        | Authentication      |
| Passlib    | Password hashing    |
| Alembic    | Database migrations |
| Uvicorn    | ASGI server         |

---

## 📁 Project Structure

```text
FastAPI-E-Commerce/
│
├── app/
│   ├── routes/
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── models.py
│   │
│   ├── schemas.py
│   │
│   ├── database.py
│   │
│   ├── dependencies.py
│   │
│   ├── seed_products.py
│   │
│   └── main.py
│
├── tests/
│
├── alembic/
├── tests/ # Coming soon
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/MojtabaOnTheNet/FastAPI-E-Commerce.git
cd FastAPI-E-Commerce
```

### 2. Create and activate a virtual environment

#### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔧 Environment Variables

Create a `.env` file in the root directory:

```env

SECRET_KEY=your_secret_key_here
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=supersecurepassword
```

---

## 🗄️ Database Setup

Run migrations:

```bash
alembic upgrade head
```

Or create tables directly (depending on your setup):

```bash
python -m app.initial_data
```

---

## ▶️ Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 📖 API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 🔑 Authentication

Authentication is handled using JWT access tokens.

### Login

```http
POST /login/access-token
```

Example response:

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

Include the token in protected requests:

```http
Authorization: Bearer your_token_here
```

---

## 🛍️ Core Features

### Users

- Register account
- Login
- Update profile
- Change password

### Products

- Create products
- Retrieve products
- Update products
- Delete products
- Product catalog browsing

### Cart

- Add products to cart
- Update quantities
- Remove products
- View cart contents
- Calculate total cart value

### Orders

- Checkout cart
- Create orders
- View order history
- Retrieve order details

### Admin

- Manage users
- Manage products
- Access any user's cart or orders
- Administrative CRUD operations

---

## 📌 Design Highlights

### Clean API Structure

The application separates:

- Routes
- Models
- Schemas
- Security
- Database configuration

making the codebase easier to maintain and extend.

### Database Relationships

Examples include:

```text
User
 ├── Cart
 │    └── CartItems
 │          └── Product
 │
 └── Orders
      └── OrderItems
            └── Product
```

### Security

- Password hashing
- JWT authentication
- Protected routes
- Role-based permissions
- Secure environment variable management

---

## 🚀 Future Improvements

- Product categories
- Product reviews and ratings
- Inventory management
- Email verification
- Password reset emails
- Redis caching
- Docker support
- Comprehensive test coverage
- Background task processing

---

## 📸 Example Workflow

1. Register a user
2. Login and obtain JWT token
3. Browse products
4. Add products to cart
5. Review cart
6. Checkout
7. Create order
8. View order history

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Mojtaba Alizadeh**

GitHub: https://github.com/MojtabaOnTheNet

Built as a portfolio project to demonstrate backend development skills using FastAPI, SQLModel, authentication, database design, and REST API best practices.

---

⭐ If you found this project useful, consider giving it a star.
