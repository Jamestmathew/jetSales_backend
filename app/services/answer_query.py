
from supabase import Client

from app.services.query_dispatcher import dispatch_query
from app.services.context_builder import build_context
from app.services.llm import generate_answer
from app.services.offerings import get_recommendation_candidates


def extract_products(structured_data):
    """
    Extract customer-facing offering cards from structured data.

    Supports:
    - Recommendation lists
    - Product catalog lists
    - Individual offering results
    - Nested offering details

    Database records remain the source of truth.
    """

    if structured_data is None:
        return []

    if isinstance(structured_data, list):
        items = structured_data
    elif isinstance(structured_data, dict):
        items = [structured_data]
    else:
        return []

    products = []
    seen_ids = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        # Recommendation result: {"offering": {...}, "score": ...}
        offering = item.get("offering")

        if isinstance(offering, dict):
            candidate = offering
        elif item.get("name") and item.get("id"):
            candidate = item
        else:
            continue

        offering_id = candidate.get("id")

        if offering_id and offering_id in seen_ids:
            continue

        if offering_id:
            seen_ids.add(offering_id)

        product_details = candidate.get("product_details")

        if isinstance(product_details, list):
            product_details = (
                product_details[0] if product_details else {}
            )

        product_details = product_details or {}

        products.append({
            "id": offering_id,
            "name": candidate.get("name"),
            "type": candidate.get("type"),
            "price": candidate.get("price"),
            "currency": candidate.get("currency"),
            "available": candidate.get("available"),
            "quantity": candidate.get(
                "quantity",
                product_details.get("quantity"),
            ),
            "image_url": candidate.get("image_url"),
        })

    return products


def answer_query(
    question: str,
    tenant_id: str,
    db: Client,
):
    """
    Process a customer question from start to finish.

    If normal retrieval returns no useful context, retrieve
    verified offerings belonging to the current tenant and
    explicitly tell the LLM that fallback mode is active.
    """

    dispatch_result = dispatch_query(
        query=question,
        tenant_id=tenant_id,
        db=db,
    )

    route = dispatch_result["route"]

    structured_data = None
    rag_results = None

    if route == "structured":
        structured_result = dispatch_result["data"]

        if structured_result.get("found"):
            structured_data = structured_result["data"]

    elif route == "rag":
        rag_results = dispatch_result["data"]

    elif route == "hybrid":
        structured_result = dispatch_result["structured_data"]
        rag_results = dispatch_result["rag_data"]

        if structured_result.get("found"):
            structured_data = structured_result["data"]

    context = build_context(
        structured_data=structured_data,
        rag_results=rag_results,
    )

    fallback_mode = False

    # Use tenant-specific offerings when normal retrieval
    # does not provide context.
    if context is None:
        fallback_offerings = get_recommendation_candidates(
            tenant_id=tenant_id,
            db=db,
        )

        if fallback_offerings:
            fallback_context = build_context(
                structured_data=fallback_offerings,
            )

            if fallback_context is not None:
                context = fallback_context
                structured_data = fallback_offerings
                fallback_mode = True

    if context is None:
        return {
            "answer": (
                "I can't confirm that specific request from "
                "the information currently available. Could "
                "you tell me more about what you're looking "
                "for so I can help clarify your options?"
            ),
            "products": [],
        }

    answer = generate_answer(
        question=question,
        context=context,
        fallback_mode=fallback_mode,
    )

    products = extract_products(
        structured_data=structured_data,
    )

    return {
        "answer": answer,
        "products": products,
    }
