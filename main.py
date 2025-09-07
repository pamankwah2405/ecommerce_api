from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from pydantic import BaseModel, Field

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection
from passlib.context import CryptContext

# Import the single database instance from db.py
from db import ecommerce_db

# Create a FastAPI application
app = FastAPI()

# Password Hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# --- Pydantic Models ---


# Dependency to get database collections
def get_users_collection() -> Collection:
    return ecommerce_db["users"]


def get_products_collection() -> Collection:
    return ecommerce_db["products"]


def get_carts_collection() -> Collection:
    return ecommerce_db["carts"]


def get_orders_collection() -> Collection:
    return ecommerce_db["orders"]


# Define the user model
class User(BaseModel):
    name: str
    email: str
    password: str


# Define the product model
class Product(BaseModel):
    name: str
    description: str
    price: float
    stock: int


# Define the cart item model
class CartItem(BaseModel):
    product_id: str = Field(..., alias="productId")
    quantity: int


# --- API Endpoints ---
@app.get("/", tags=["Home"])
def home_page():
    return {"message": "Welcome to our E-commerce API"}


@app.post("/register")
def register_user(user: User, users_collection: Collection = Depends(get_users_collection)):
    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before storing
    hashed_password = pwd_context.hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password

    # Insert user and get the ID from the result
    result = users_collection.insert_one(user_data)
    user_id = str(result.inserted_id)
    return {"message": "User registered successfully", "user_id": user_id}


@app.post("/login")
def login_user(user: User, users_collection: Collection = Depends(get_users_collection)):
    user_doc = users_collection.find_one({"email": user.email})

    # Verify user exists and the provided password matches the stored hash
    if user_doc and pwd_context.verify(user.password, user_doc["password"]):
        user_id = str(user_doc["_id"])
        return {"message": "User logged in successfully", "user_id": user_id}

    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.get("/products")
def fetch_all_available_products(
    products_collection: Collection = Depends(get_products_collection),
):
    """Fetch all available products"""
    products = list(products_collection.find())
    for product in products:
        product["_id"] = str(product["_id"])
    return {"products": products}


@app.get("/products/{product_id}")
def get_product(
    product_id: str, products_collection: Collection = Depends(get_products_collection)
):
    """Fetch product by ID"""
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if product:
            product["_id"] = str(product["_id"])
            return {"product": product}
        raise HTTPException(status_code=404, detail="Product not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")


@app.post("/cart", status_code=200)
def add_to_cart(
    user_id: str, item: CartItem, carts_collection: Collection = Depends(get_carts_collection)
):
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    cart = carts_collection.find_one(
        {"user_id": user_obj_id, "items.productId": item.product_id}
    )

    if cart:
        # If it exists, increment the quantity
        carts_collection.update_one(
            {"user_id": user_obj_id, "items.productId": item.product_id},
            {"$inc": {"items.$.quantity": item.quantity}},
        )
    else:
        # If it doesn't exist, add it to the cart (creating the cart if necessary)
        carts_collection.update_one(
            {"user_id": user_obj_id},
            {"$push": {"items": item.dict(by_alias=True)}},
            upsert=True,
        )
    return {"message": "Item added to cart"}


@app.get("/cart")
def get_cart(
    user_id: str,
    carts_collection: Collection = Depends(get_carts_collection),
    products_collection: Collection = Depends(get_products_collection),
):
    try:
        cart = carts_collection.find_one({"user_id": ObjectId(user_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if not cart or not cart.get("items"):
        return {"cart": {"products": [], "total": 0}}

    products = []
    total_price = 0
    for item in cart.get("items", []):
        product = products_collection.find_one({"_id": ObjectId(item["productId"])})
        if product:
            subtotal = product["price"] * item["quantity"]
            total_price += subtotal
            products.append(
                {
                    "product_id": str(product["_id"]),
                    "name": product["name"],
                    "quantity": item["quantity"],
                    "unit_price": product["price"],
                    "subtotal": subtotal,
                }
            )
    return {"cart": {"products": products, "total": total_price}}


@app.post("/checkout")
def checkout(
    user_id: str,
    carts_collection: Collection = Depends(get_carts_collection),
    products_collection: Collection = Depends(get_products_collection),
    orders_collection: Collection = Depends(get_orders_collection),
):
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    cart = carts_collection.find_one({"user_id": user_obj_id})

    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = {"user_id": user_obj_id, "products": [], "total": 0}
    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["productId"])})
        if product:
            if product["stock"] < item["quantity"]:
                raise HTTPException(
                    status_code=400, detail=f"Not enough stock for {product['name']}"
                )

            order["products"].append(
                {"productId": item["productId"], "quantity": item["quantity"]}
            )
            order["total"] += product["price"] * item["quantity"]

            # Decrement stock for the purchased product
            products_collection.update_one(
                {"_id": product["_id"]}, {"$inc": {"stock": -item["quantity"]}}
            )

    order_id = orders_collection.insert_one(order).inserted_id

    # Clear the user's cart after successful checkout
    carts_collection.delete_one({"user_id": user_obj_id})

    return {
        "message": "Order placed successfully",
        "order_id": str(order_id),
        "total": order["total"],
    }


# Admin Flow
@app.post("/add_product", tags=["Admin"])
def add_product(
    product: Product, products_collection: Collection = Depends(get_products_collection)
):
    products_collection.insert_one(product.dict())
    return {"message": "Product added successfully"}


@app.put("/products/{product_id}", tags=["Admin"])
def update_product(
    product_id: str,
    product: Product,
    products_collection: Collection = Depends(get_products_collection),
):
    try:
        result = products_collection.update_one(
            {"_id": ObjectId(product_id)}, {"$set": product.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product updated successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")


@app.delete("/products/{product_id}", tags=["Admin"])
def delete_product(
    product_id: str, products_collection: Collection = Depends(get_products_collection)
):
    try:
        result = products_collection.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")


if __name__ == "__main__":
    # Use uvicorn to run the app
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)