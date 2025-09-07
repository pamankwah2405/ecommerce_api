# E-commerce REST API

Hi! I built this **FastAPI-based E-commerce API** to practice creating a full backend for an online store. It handles user authentication, product management, shopping carts, and order checkout. The API is simple, efficient, and designed to be easy to extend for any small to medium e-commerce project.

---

## Features

-   **User Authentication:** Secure user registration and login with password hashing (bcrypt).
-   **Product Management:** CRUD operations for products, accessible by admins.
-   **Shopping Cart:** Add items to a user-specific cart and view cart contents.
-   **Checkout:** Convert a cart into an order while updating product stock.
-   **Data Validation:** Requests and responses are validated using Pydantic models.
-   **High Performance:** Built with FastAPI for async operations and fast responses.

---

## Technologies Used

-   **Backend:** FastAPI
-   **Database:** MongoDB with PyMongo
-   **Data Validation:** Pydantic
-   **Password Hashing:** Passlib using `bcrypt`
-   **Environment Variables:** python-dotenv
-   **ASGI Server:** Uvicorn

---

## Setup and Installation

Follow these steps to run the API on your local machine.

### 1. Prerequisites

-   Python 3.8+
-   MongoDB (local instance or a free MongoDB Atlas cluster)

### 2. Clone the Repository

```bash
git clone https://github.com/pamankwah2405/ecommerce_api2.git
cd ecommerce_api2
```

### 3. Create a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Create a `requirements.txt` file with the following content:

```
fastapi
uvicorn[standard]
pymongo
passlib[bcrypt]
pydantic
python-dotenv
```

Then, install the dependencies using pip:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory of the project and add your MongoDB connection details.

```env
MONGO_URI="mongodb://localhost:27017/"
DB_NAME="ecommerce_db"
```

Replace the `MONGO_URI` with your own MongoDB connection string if you are using a remote database like MongoDB Atlas.

### 6. Run the API

Start the development server using Uvicorn.

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. The `--reload` flag automatically restarts the server when you make changes to the code.

You can access the interactive API documentation (powered by Swagger UI) at `http://127.0.0.1:8000/docs`.

---

## API Endpoints

The API provides the following endpoints. You can test them all from the `/docs` page.

### User Authentication

-   **`POST /register`**: Register a new user.
    -   **Request Body:**
        ```json
        {
          "name": "John Doe",
          "email": "john.doe@example.com",
          "password": "securepassword123"
        }
        ```
-   **`POST /login`**: Log in an existing user.
    -   **Request Body:**
        ```json
        {
          "email": "john.doe@example.com",
          "password": "securepassword123"
        }
        ```

### Products

-   **`GET /products`**: Fetch all available products.
-   **`GET /products/{product_id}`**: Fetch a single product by its ID.

### Shopping Cart

-   **`POST /cart`**: Add an item to the user's shopping cart.
    -   **Query Parameter:** `user_id`
    -   **Request Body:**
        ```json
        {
          "productId": "product_id_here",
          "quantity": 1
        }
        ```
-   **`GET /cart`**: View the contents of a user's cart, including subtotal and total price.
    -   **Query Parameter:** `user_id`

### Checkout

-   **`POST /checkout`**: Place an order from the items in the cart. This will create an order, clear the cart, and update product stock.
    -   **Query Parameter:** `user_id`

### Admin

These endpoints are tagged for administrative purposes.

-   **`POST /add_product`**: Add a new product to the store.
    -   **Request Body:**
        ```json
        {
          "name": "Laptop",
          "description": "A powerful new laptop.",
          "price": 1200.50,
          "stock": 50
        }
        ```
-   **`PUT /products/{product_id}`**: Update an existing product's details.
-   **`DELETE /products/{product_id}`**: Remove a product from the store.

---

## Project Structure

eccomerce_api/
├── .env                # Environment variables (not committed to git)
├── db.py               # Database connection setup
├── main.py             # Main FastAPI application and endpoints
├── requirements.txt    # Project dependencies
└── README.md           # This file
