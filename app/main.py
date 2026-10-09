from fastapi import Depends, FastAPI

from app.api.documents import router as documents_router
from app.api.auth import router as auth_router
from app.api.offerings import router as offerings_router
from app.api.businesses import router as businesses_router

from app.core.security import (
    get_current_user,
    get_current_tenant,
    require_owner,
)


app = FastAPI(
    title="AI Business Assistant API"
)


app.include_router(documents_router)
app.include_router(auth_router)
app.include_router(offerings_router)
app.include_router(businesses_router)


@app.get("/")
def root():
    return {
        "message": "AI Business Assistant API is running"
    }


@app.get("/tenant")
def tenant_route(
    tenant=Depends(get_current_tenant)
):
    return tenant


@app.get("/protected")
def protected_route(
    user=Depends(get_current_user)
):
    return {
        "user_id": user.id,
        "email": user.email
    }


@app.get("/owner-test")
def owner_test(
    tenant=Depends(require_owner)
):
    return {
        "message": "Owner access granted",
        "tenant_id": tenant["tenant_id"],
        "role": tenant["role"],
        "user_id": tenant["user_id"],
    }