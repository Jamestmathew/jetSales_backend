
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

from app.core.config import (
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    access_token = credentials.credentials

    try:
        auth_client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_ROLE_KEY,
        )

        response = auth_client.auth.get_user(access_token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )

        return response.user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


def get_current_tenant(
    user=Depends(get_current_user),
):
    db = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )

    response = (
        db
        .table("user_tenants")
        .select("user_id, tenant_id, role")
        .eq("user_id", user.id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=403,
            detail="User does not belong to a tenant",
        )

    if len(response.data) != 1:
        raise HTTPException(
            status_code=500,
            detail="User tenant membership configuration is invalid",
        )

    membership = response.data[0]

    return {
        "tenant_id": membership["tenant_id"],
        "role": membership["role"],
        "user_id": user.id,
    }


def require_owner(
    tenant=Depends(get_current_tenant),
):
    if tenant["role"] != "owner":
        raise HTTPException(
            status_code=403,
            detail="Owner permissions required",
        )

    return tenant


def get_db() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )