
from supabase import Client

from app.services.offerings import (
    find_offering_from_query,
    count_products,
    get_products,
    get_product_quantity,
    get_offering_price,
    get_offering_availability,
    get_offering_description,
)

from app.services.recommendation import recommend_offerings


def detect_business_intent(query: str):
    query = query.lower()

    if any(word in query for word in [
        "price", "cost", "how much", "fee",
    ]):
        return "price"

    if any(word in query for word in [
        "how many", "quantity", "units", "stock left",
    ]):
        return "quantity"

    if any(word in query for word in [
        "available", "availability", "in stock", "stock",
    ]):
        return "availability"

    if any(phrase in query for phrase in [
        "what products",
        "which products",
        "list products",
        "products do you have",
    ]):
        return "product_list"

    if any(phrase in query for phrase in [
        "recommend",
        "recommendation",
        "what do you recommend",
        "what would you recommend",
        "which should i choose",
        "which one should i choose",
        "which product should i choose",
        "which service should i choose",
        "which is best",
        "what is the best",
        "best option",
        "best product",
        "best service",
        "what should i buy",
        "what should i use",
        "help me choose",
        "i'm looking for",
        "i am looking for",
        "looking for",
        "i need something",
        "i need a",
        "i need an",
        "i need some",
    ]):
        return "recommendation"

    if any(phrase in query for phrase in [
        "what is",
        "what's",
        "tell me about",
        "describe",
        "description",
    ]):
        return "description"

    return "general"


def search_business_data(
    query: str,
    tenant_id: str,
    db: Client,
):
    intent = detect_business_intent(query)

    # --------------------------------------------------
    # Recommendations
    # Preserve the recommendation engine's scoring.
    # --------------------------------------------------

    if intent == "recommendation":
        recommendations = recommend_offerings(
            query=query,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "found": bool(recommendations),
            "type": "recommendation",
            "intent": intent,
            "data": recommendations,
        }

    # --------------------------------------------------
    # Product collection questions
    # --------------------------------------------------

    if intent == "product_list":
        products = get_products(
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "found": True,
            "type": "product_collection",
            "intent": intent,
            "data": products,
        }

    # --------------------------------------------------
    # Count all products when no specific product is named
    # --------------------------------------------------

    if intent == "quantity":
        query_lower = query.lower()

        if "product" in query_lower or "products" in query_lower:
            offering_match = find_offering_from_query(
                query=query,
                tenant_id=tenant_id,
                db=db,
            )

            if offering_match is None:
                count = count_products(
                    tenant_id=tenant_id,
                    db=db,
                )

                return {
                    "found": True,
                    "type": "product_collection",
                    "intent": "product_count",
                    "data": {"count": count},
                }

    # --------------------------------------------------
    # Resolve a specific offering
    # --------------------------------------------------

    offering = find_offering_from_query(
        query=query,
        tenant_id=tenant_id,
        db=db,
    )

    if offering is None:
        return {
            "found": False,
            "type": None,
            "intent": intent,
            "data": None,
        }

    offering_id = offering["id"]

    # --------------------------------------------------
    # Price
    # Include the complete offering for product cards,
    # while retaining the price result for the answer.
    # --------------------------------------------------

    if intent == "price":
        price = get_offering_price(
            offering_id=offering_id,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "found": price is not None,
            "type": "offering",
            "intent": "offering_price",
            "data": {
                "offering": offering,
                "price_details": price,
            } if price is not None else None,
        }

    # --------------------------------------------------
    # Availability
    # --------------------------------------------------

    if intent == "availability":
        availability = get_offering_availability(
            offering_id=offering_id,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "found": availability is not None,
            "type": "offering",
            "intent": "offering_availability",
            "data": {
                "offering": offering,
                "availability_details": availability,
            } if availability is not None else None,
        }

    # --------------------------------------------------
    # Quantity
    # --------------------------------------------------

    if intent == "quantity":
        quantity = get_product_quantity(
            offering_id=offering_id,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "found": quantity is not None,
            "type": "offering",
            "intent": "product_quantity",
            "data": {
                "offering": offering,
                "quantity_details": quantity,
            } if quantity is not None else None,
        }

    # --------------------------------------------------
    # Description
    # --------------------------------------------------

    if intent == "description":
        description = get_offering_description(
            offering_id=offering_id,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "found": description is not None,
            "type": "offering",
            "intent": "offering_description",
            "data": {
                "offering": offering,
                "description_details": description,
            } if description is not None else None,
        }

    # --------------------------------------------------
    # Default offering response
    # --------------------------------------------------

    return {
        "found": True,
        "type": "offering",
        "intent": intent,
        "data": {"offering": offering},
    }
