from app.core.supabase import create_db_client
from app.services.offerings import get_offering_price


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

OFFERING_ID = "caa692ed-82a2-46d2-83a5-e2abf18fac1d"


db = create_db_client()


result = get_offering_price(
    offering_id=OFFERING_ID,
    tenant_id=TENANT_ID,
    db=db,
)


print("Offering price:")
print(result)
