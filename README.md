# E-commerce Store

A modern e-commerce platform built with Django , responsive UI with Tailwind CSS.

## Features


### Shopping Experience
- User authentication (signup/login)
- Shopping cart 
- Size selection
-  stock updates


## Tech Stack

- **Backend**:
  - Django 5.1
  - FastAPI
  - SQLite Database

- **Frontend**:
  - Tailwind CSS
  - JavaScripe

- **Authentication**:
  - Django Authentication System

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ecommerce
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Add default sizes:
```bash
python manage.py add_default_sizes
```

7. Run the development server:
```bash
python manage.py runserver
```





### Products
- `GET /api/v1/products/` - List all products
- `GET /api/v1/products/{id}/` - Get product details
- `POST /api/v1/products/` - Create new product (admin only)
- `PUT /api/v1/products/{id}/` - Update product (admin only)
- `DELETE /api/v1/products/{id}/` - Delete product (admin only)

### Web Routes
- `/` - Product listing
- `/product/{id}/` - Product detail
- `/cart/` - Shopping cart
- `/login/` - User login
- `/signup/` - User registration
- `/profile/` - User profile
