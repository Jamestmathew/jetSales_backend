from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import (
    get_current_tenant,
    require_owner,
    get_db,
)


router = APIRouter(
    prefix="/businesses",
    tags=["Businesses"],
)


class BusinessCreate(BaseModel):
    name: str
    description: str | None = None
    phone: str | None = None
    email: str | None = None
    whatsapp: str | None = None
    address: str | None = None
    website: str | None = None
    business_hours: str | None = None


class BusinessUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    phone: str | None = None
    email: str | None = None
    whatsapp: str | None = None
    address: str | None = None
    website: str | None = None
    business_hours: str | None = None


@router.post("/")
def create_business(
    data: BusinessCreate,
    tenant=Depends(require_owner),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    response = (
        db
        .table("businesses")
        .insert({
            "tenant_id": tenant_id,
            **data.model_dump(),
        })
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create business",
        )

    return {
        "message": "Business created successfully",
        "business": response.data[0],
    }


@router.get("/")
def get_businesses(
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    response = (
        db
        .table("businesses")
        .select("*")
        .eq("tenant_id", tenant_id)
        .execute()
    )

    return {
        "businesses": response.data,
    }


@router.get("/{business_id}")
def get_business(
    business_id: str,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    response = (
        db
        .table("businesses")
        .select("*")
        .eq("id", business_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    return {
        "business": response.data[0],
    }


@router.patch("/{business_id}")
def update_business(
    business_id: str,
    data: BusinessUpdate,
    tenant=Depends(require_owner),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    existing = (
        db
        .table("businesses")
        .select("id")
        .eq("id", business_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    response = (
        db
        .table("businesses")
        .update(update_data)
        .eq("id", business_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to update business",
        )

    return {
        "message": "Business updated successfully",
        "business": response.data[0],
    }


@router.delete("/{business_id}")
def delete_business(
    business_id: str,
    tenant=Depends(require_owner),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    existing = (
        db
        .table("businesses")
        .select("id")
        .eq("id", business_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    response = (
        db
        .table("businesses")
        .delete()
        .eq("id", business_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete business",
        )

    return {
        "message": "Business deleted successfully",
        "business_id": business_id,
    }
