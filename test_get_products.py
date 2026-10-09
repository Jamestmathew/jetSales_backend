from app.core.supabase import create_db_client
from app.services.offerings import get_products

TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()

result = get_products(
    tenant_id=TENANT_ID,
    db=db,
)

print("Products:")
for product in result:
    print(product)