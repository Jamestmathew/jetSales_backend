from supabase import Client


def search_offerings(
    query: str,
    tenant_id: str,
    db: Client,
):
    response = (
        db.table("offerings")
        .select(
            """
            id,
            business_id,
            name,
            type,
            description,
            price,
            currency,
            available,
            image_url,
            product_details (
                quantity,
                sku
            )
            """
        )
        .eq("tenant_id", tenant_id)
        .ilike("name", f"%{query}%")
        .limit(10)
        .execute()
    )

    results = []

    for offering in response.data:
        product_details = offering.get("product_details")

        if isinstance(product_details, list):
            product_details = (
                product_details[0]
                if product_details
                else None
            )

        results.append({
            "id": offering["id"],
            "business_id": offering["business_id"],
            "name": offering["name"],
            "type": offering["type"],
            "description": offering["description"],
            "price": offering["price"],
            "currency": offering["currency"],
            "available": offering["available"],
            "image_url": offering["image_url"],
            "quantity": (
                product_details["quantity"]
                if product_details
                else None
            ),
            "sku": (
                product_details["sku"]
                if product_details
                else None
            ),
        })

    return results


def get_offering(
    offering_id: str,
    tenant_id: str,
    db: Client,
):
    response = (
        db.table("offerings")
        .select(
            """
            id,
            business_id,
            name,
            type,
            description,
            price,
            currency,
            available,
            image_url,
            product_details (
                quantity,
                sku
            )
            """
        )
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    offering = response.data[0]

    product_details = offering.get("product_details")

    if isinstance(product_details, list):
        product_details = (
            product_details[0]
            if product_details
            else None
        )

    return {
        "id": offering["id"],
        "business_id": offering["business_id"],
        "name": offering["name"],
        "type": offering["type"],
        "description": offering["description"],
        "price": offering["price"],
        "currency": offering["currency"],
        "available": offering["available"],
        "image_url": offering["image_url"],
        "quantity": (
            product_details["quantity"]
            if product_details
            else None
        ),
        "sku": (
            product_details["sku"]
            if product_details
            else None
        ),
    }


def find_offering_from_query(
    query: str,
    tenant_id: str,
    db: Client,
):
    """
    Find an offering mentioned in a customer query.

    Matching order:

    1. Exact offering name
    2. Normalized offering name
    3. Exact / normalized alias

    Returns:
        offering dict if a confident match is found
        None if no confident match is found
    """

    response = (
        db.table("offerings")
        .select(
            """
            id,
            business_id,
            name,
            type,
            description,
            price,
            currency,
            available,
            image_url,
            aliases,
            product_details (
                quantity,
                sku
            )
            """
        )
        .eq("tenant_id", tenant_id)
        .limit(50)
        .execute()
    )

    if not response.data:
        return None

    offerings = []

    for offering in response.data:
        product_details = offering.get("product_details")

        if isinstance(product_details, list):
            product_details = (
                product_details[0]
                if product_details
                else None
            )

        offerings.append({
            "id": offering["id"],
            "business_id": offering["business_id"],
            "name": offering["name"],
            "type": offering["type"],
            "description": offering["description"],
            "price": offering["price"],
            "currency": offering["currency"],
            "available": offering["available"],
            "image_url": offering["image_url"],
            "aliases": offering.get("aliases") or [],
            "quantity": (
                product_details["quantity"]
                if product_details
                else None
            ),
            "sku": (
                product_details["sku"]
                if product_details
                else None
            ),
        })

    # --------------------------------------------------
    # Normalization helper
    # --------------------------------------------------

    def normalize(text: str):
        return " ".join(
            text.lower()
            .replace("-", " ")
            .replace("_", " ")
            .split()
        )

    normalized_query = normalize(query)
    query_lower = query.lower().strip()

    # --------------------------------------------------
    # 1. Exact offering name match
    # --------------------------------------------------

    for offering in offerings:
        name = offering["name"].lower().strip()

        if name in query_lower:
            return offering

    # --------------------------------------------------
    # 2. Normalized offering name match
    # --------------------------------------------------

    for offering in offerings:
        normalized_name = normalize(offering["name"])

        if normalized_name in normalized_query:
            return offering

    # --------------------------------------------------
    # 3. Exact / normalized alias match
    # --------------------------------------------------

    for offering in offerings:
        for alias in offering["aliases"]:
            normalized_alias = normalize(alias)

            if normalized_alias in normalized_query:
                return offering

    # --------------------------------------------------
    # No confident offering match
    # --------------------------------------------------

    return None


def count_products(
    tenant_id: str,
    db: Client,
):
    response = (
        db
        .table("offerings")
        .select("id", count="exact")
        .eq("tenant_id", tenant_id)
        .eq("type", "product")
        .execute()
    )

    return response.count or 0


def get_products(
    tenant_id: str,
    db: Client,
):
    response = (
        db
        .table("offerings")
        .select(
            """
            id,
            business_id,
            name,
            type,
            description,
            price,
            currency,
            available,
            image_url,
            product_details (
                quantity,
                sku
            )
            """
        )
        .eq("tenant_id", tenant_id)
        .eq("type", "product")
        .execute()
    )

    products = []

    for offering in response.data:
        product_details = offering.get("product_details")

        if isinstance(product_details, list):
            product_details = (
                product_details[0]
                if product_details
                else None
            )

        products.append({
            "id": offering["id"],
            "business_id": offering["business_id"],
            "name": offering["name"],
            "type": offering["type"],
            "description": offering["description"],
            "price": offering["price"],
            "currency": offering["currency"],
            "available": offering["available"],
            "image_url": offering["image_url"],
            "quantity": (
                product_details["quantity"]
                if product_details
                else None
            ),
            "sku": (
                product_details["sku"]
                if product_details
                else None
            ),
        })

    return products


def get_product_quantity(
    offering_id: str,
    tenant_id: str,
    db: Client,
):
    response = (
        db
        .table("offerings")
        .select(
            """
            id,
            name,
            type,
            product_details (
                quantity
            )
            """
        )
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .eq("type", "product")
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    offering = response.data[0]

    product_details = offering.get("product_details")

    if isinstance(product_details, list):
        product_details = (
            product_details[0]
            if product_details
            else None
        )

    return {
        "offering_id": offering["id"],
        "name": offering["name"],
        "quantity": (
            product_details["quantity"]
            if product_details
            else None
        ),
    }


def get_offering_price(
    offering_id: str,
    tenant_id: str,
    db: Client,
):
    response = (
        db
        .table("offerings")
        .select(
            """
            id,
            name,
            type,
            price,
            currency
            """
        )
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    offering = response.data[0]

    return {
        "offering_id": offering["id"],
        "name": offering["name"],
        "type": offering["type"],
        "price": offering["price"],
        "currency": offering["currency"],
    }


def get_offering_availability(
    offering_id: str,
    tenant_id: str,
    db: Client,
):
    response = (
        db
        .table("offerings")
        .select(
            """
            id,
            name,
            type,
            available
            """
        )
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    offering = response.data[0]

    return {
        "offering_id": offering["id"],
        "name": offering["name"],
        "type": offering["type"],
        "available": offering["available"],
    }


def get_offering_description(
    offering_id: str,
    tenant_id: str,
    db: Client,
):
    response = (
        db
        .table("offerings")
        .select(
            """
            id,
            name,
            type,
            description
            """
        )
        .eq("id", offering_id)
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    offering = response.data[0]

    return {
        "offering_id": offering["id"],
        "name": offering["name"],
        "type": offering["type"],
        "description": offering["description"],
    }

def get_recommendation_candidates(
    tenant_id: str,
    db: Client,
):
    response = (
        db
        .table("offerings")
        .select(
            """
            id,
            business_id,
            name,
            type,
            description,
            price,
            currency,
            available,
            image_url,
            aliases,
            product_details (
                quantity,
                sku
            )
            """
        )
        .eq("tenant_id", tenant_id)
        .execute()
    )

    candidates = []

    for offering in response.data:
        product_details = offering.get("product_details")

        if isinstance(product_details, list):
            product_details = (
                product_details[0]
                if product_details
                else None
            )

        candidates.append({
            "id": offering["id"],
            "business_id": offering["business_id"],
            "name": offering["name"],
            "type": offering["type"],
            "description": offering["description"],
            "price": offering["price"],
            "currency": offering["currency"],
            "available": offering["available"],
            "image_url": offering["image_url"],
            "aliases": offering.get("aliases") or [],
            "quantity": (
                product_details["quantity"]
                if product_details
                else None
            ),
            "sku": (
                product_details["sku"]
                if product_details
                else None
            ),
        })

    return candidates