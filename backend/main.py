import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product as ProductSchema, Order as OrderSchema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Campus commerce backend running"}


# Utility to convert ObjectId to string in results

def _serialize(doc):
    doc = dict(doc)
    if doc.get("_id"):
        doc["id"] = str(doc.pop("_id"))
    return doc


# Products -----------------------------------------------------------------

@app.post("/products")
def create_product(product: ProductSchema):
    try:
        product_id = create_document("product", product)
        return {"id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products")
def list_products(category: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    try:
        filt = {}
        if category:
            filt["category"] = category
        if q:
            # Simple text search across fields
            filt["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
            ]
        docs = get_documents("product", filt, limit)
        return [_serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/seed")
def seed_products():
    """Insert demo products if collection is empty"""
    try:
        existing = get_documents("product", {}, limit=1)
        if existing:
            return {"status": "ok", "message": "Products already exist"}
        demo_products = [
            {
                "title": "Maggi Bowl (Hot & Fresh)",
                "description": "Cooked to order at the canteen. Pickup in 10 mins.",
                "price": 45,
                "category": "Food",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1526318472351-c75fcf070305?q=80&w=1200&auto=format&fit=crop",
                "seller_name": "Campus Canteen"
            },
            {
                "title": "Data Structures Notes (PDF)",
                "description": "Second-year topper notes. Clean and concise.",
                "price": 79,
                "category": "Notes",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?q=80&w=1200&auto=format&fit=crop",
                "seller_name": "Ananya (CSE)"
            },
            {
                "title": "College Hoodie (Navy)",
                "description": "Official club merchandise. Sizes S-XL.",
                "price": 999,
                "category": "Merch",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1548883354-7622d03aca27?q=80&w=1200&auto=format&fit=crop",
                "seller_name": "Design Club"
            },
            {
                "title": "Event Pass - Battle of Bands",
                "description": "Entry ticket for Saturday 7 PM, Auditorium.",
                "price": 199,
                "category": "Events",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?q=80&w=1200&auto=format&fit=crop",
                "seller_name": "Music Club"
            },
            {
                "title": "Exam Kit (Pens + Highlighter)",
                "description": "Everything you need for finals week.",
                "price": 129,
                "category": "Stationery",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1481070555726-e2fe8357725c?q=80&w=1200&auto=format&fit=crop",
                "seller_name": "Stationery Shop"
            }
        ]
        for p in demo_products:
            create_document("product", p)
        return {"status": "ok", "inserted": len(demo_products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Orders --------------------------------------------------------------------

@app.post("/orders")
def create_order(order: OrderSchema):
    # Compute total to prevent tampering from client
    computed_total = sum(item.price * item.quantity for item in order.items)
    if abs(computed_total - order.total_amount) > 0.01:
        raise HTTPException(status_code=400, detail="Invalid total amount")
    try:
        order_id = create_document("order", order)
        return {"id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
