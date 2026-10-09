
from app.core.security import get_db
from app.services.offerings import get_products

# JetIntel tenant ID — use only for this local diagnostic.
tenant_id = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

try:
    db = get_db()
    products = get_products(tenant_id, db)

    print("Product retrieval succeeded.")
    print("Number of products:", len(products))

    for product in products:
        print({
            "name": product["name"],
            "price": product["price"],
            "currency": product["currency"],
            "available": product["available"],
        })

except Exception as error:
    print("Product retrieval failed.")
    print("Error type:", type(error).__name__)
    print("Error message:", str(error))
