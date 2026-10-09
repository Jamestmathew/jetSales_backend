
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import (
    get_current_tenant,
    require_owner,
    get_db,
)

from app.services.offerings import (
    search_offerings as search_offerings_service,
    get_offering,
)

from app.services.business_query import search_business_data


router = APIRouter(
    prefix="/offerings",
    tags=["Offerings"],
)


# ============================================================
# Request Models
# ============================================================

class ProductDetails(BaseModel):
    quantity: int | None = Field(default=None, ge=0)
    sku: str | None = None


class OfferingCreate(BaseModel):
    business_id: str
    name: str
    type: Literal["product", "service"]
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    currency: str = "NGN"
    available: bool = True
    image_url: str | None = None
    aliases: list[str] = Field(default_factory=list)
    product_details: ProductDetails | None = None


class OfferingUpdate(BaseModel):
    business_id: str | None = None
    name: str | None = None
    type: Literal["product", "service"] | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    currency: str | None = None
    available: bool | None = None
    image_url: str | None = None
    aliases: list[str] | None = None
    product_details: ProductDetails | None = None


# ============================================================
# Helpers
# ============================================================

def verify_business_belongs_to_tenant(
    business_id: str,
    tenant_id: str,
    db,
):
    response = (
        db
        .table("businesses")
        .select("id")
        .eq("id", business_id)
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )


def get_product_details(
    offering_id: str,
    db,
):
    response = (
        db
        .table("product_details")
        .select(
            "offering_id, quantity, sku, created_at"
        )
        .eq("offering_id", offering_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


# ============================================================
# Create Offering
# ============================================================

@router.post("/")
def create_offering(
    data: OfferingCreate,
    tenant=Depends(require_owner),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    verify_business_belongs_to_tenant(
        business_id=data.business_id,
        tenant_id=tenant_id,
        db=db,
    )

    if (
        data.type == "service"
        and data.product_details is not None
    ):
        raise HTTPException(
            status_code=400,
            detail="Services cannot have product details",
        )

    offering_data = {
        "tenant_id": tenant_id,
        "business_id": data.business_id,
        "name": data.name,
        "type": data.type,
        "description": data.description,
        "price": data.price,
        "currency": data.currency,
        "available": data.available,
        "image_url": data.image_url,
        "aliases": data.aliases,
    }

    response = (
        db
        .table("offerings")
        .insert(offering_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create offering",
        )

    offering = response.data[0]

    if (
        data.type == "product"
        and data.product_details is not None
    ):
        product_details_response = (
            db
            .table("product_details")
            .insert({
                "offering_id": offering["id"],
                "quantity": data.product_details.quantity,
                "sku": data.product_details.sku,
            })
            .execute()
        )

        if not product_details_response.data:
            raise HTTPException(
                status_code=500,
                detail="Offering created but product details failed",
            )

        offering["product_details"] = (
            product_details_response.data[0]
        )

    else:
        offering["product_details"] = None

    return {
        "message": "Offering created successfully",
        "offering": offering,
    }


# ============================================================
# List Offerings
# ============================================================

@router.get("/")
def get_offerings(
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    response = (
        db
        .table("offerings")
        .select("*")
        .eq("tenant_id", tenant_id)
        .order("created_at", desc=False)
        .execute()
    )

    offerings = response.data

    for offering in offerings:
        offering["product_details"] = get_product_details(
            offering_id=offering["id"],
            db=db,
        )

    return {
        "offerings": offerings,
    }


# ============================================================
# Search Offerings
# ============================================================

@router.get("/search")
def search_offerings(
    query: str,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    results = search_offerings_service(
        query=query,
        tenant_id=tenant["tenant_id"],
        db=db,
    )

    return {
        "found": len(results) > 0,
        "results": results,
    }


# ============================================================
# Business Search
# ============================================================

@router.get("/business-search")
def business_search(
    query: str,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    return search_business_data(
        query=query,
        tenant_id=tenant["tenant_id"],
        db=db,
    )


# ============================================================
# Get One Offering
# ============================================================

@router.get("/{offering_id}")
def get_offering_route(
    offering_id: str,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    offering = get_offering(
        offering_id=offering_id,
        tenant_id=tenant["tenant_id"],
        db=db,
    )

    if offering is None:
        raise HTTPException(
            status_code=404,
            detail="Offering not found",
        )

    offering["product_details"] = get_product_details(
        offering_id=offering_id,
        db=db,
    )

    return {
        "found": True,
        "offering": offering,
    }


# ============================================================
# Update Offering
# ============================================================

@router.patch("/{offering_id}")
def update_offering(
    offering_id: str,
    data: OfferingUpdate,
    tenant=Depends(require_owner),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    existing_response = (
        db
        .table("offerings")
        .select("*")
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if not existing_response.data:
        raise HTTPException(
            status_code=404,
            detail="Offering not found",
        )

    existing = existing_response.data[0]

    update_data = data.model_dump(
        exclude_unset=True,
        exclude={"product_details"},
    )

    if "business_id" in update_data:
        verify_business_belongs_to_tenant(
            business_id=update_data["business_id"],
            tenant_id=tenant_id,
            db=db,
        )

    new_type = update_data.get(
        "type",
        existing["type"],
    )

    if (
        new_type == "service"
        and data.product_details is not None
    ):
        raise HTTPException(
            status_code=400,
            detail="Services cannot have product details",
        )

    if (
        not update_data
        and data.product_details is None
    ):
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    if update_data:
        response = (
            db
            .table("offerings")
            .update(update_data)
            .eq("id", offering_id)
            .eq("tenant_id", tenant_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to update offering",
            )

        offering = response.data[0]

    else:
        offering = existing

    # ========================================================
    # Product Details Management
    # ========================================================

    if new_type == "service":

        (
            db
            .table("product_details")
            .delete()
            .eq("offering_id", offering_id)
            .execute()
        )

        offering["product_details"] = None

    elif data.product_details is not None:

        existing_details = get_product_details(
            offering_id=offering_id,
            db=db,
        )

        details_data = {
            "offering_id": offering_id,
            "quantity": data.product_details.quantity,
            "sku": data.product_details.sku,
        }

        if existing_details:

            details_response = (
                db
                .table("product_details")
                .update({
                    "quantity": data.product_details.quantity,
                    "sku": data.product_details.sku,
                })
                .eq("offering_id", offering_id)
                .execute()
            )

        else:

            details_response = (
                db
                .table("product_details")
                .insert(details_data)
                .execute()
            )

        if not details_response.data:
            raise HTTPException(
                status_code=500,
                detail="Offering updated but product details failed",
            )

        offering["product_details"] = (
            details_response.data[0]
        )

    else:
        offering["product_details"] = get_product_details(
            offering_id=offering_id,
            db=db,
        )

    return {
        "message": "Offering updated successfully",
        "offering": offering,
    }


# ============================================================
# Delete Offering
# ============================================================

@router.delete("/{offering_id}")
def delete_offering(
    offering_id: str,
    tenant=Depends(require_owner),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    existing_response = (
        db
        .table("offerings")
        .select("id")
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if not existing_response.data:
        raise HTTPException(
            status_code=404,
            detail="Offering not found",
        )

    # Remove product details first.
    (
        db
        .table("product_details")
        .delete()
        .eq("offering_id", offering_id)
        .execute()
    )

    response = (
        db
        .table("offerings")
        .delete()
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete offering",
        )

    return {
        "message": "Offering deleted successfully",
        "offering_id": offering_id,
    }
