from supabase import Client

from app.services.query_router import route_query
from app.services.business_query import search_business_data
from app.services.rag import search_documents


def dispatch_query(query: str, tenant_id: str, db: Client):
    route = route_query(query)

    if route["route"] == "structured":
        result = search_business_data(
            query=query,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "route": "structured",
            "intent": route["intent"],
            "data": result,
        }

    if route["route"] == "rag":
        results = search_documents(
            query=query,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "route": "rag",
            "intent": route["intent"],
            "data": results,
        }

    if route["route"] == "hybrid":
        structured_result = search_business_data(
            query=query,
            tenant_id=tenant_id,
            db=db,
        )

        rag_results = search_documents(
            query=query,
            tenant_id=tenant_id,
            db=db,
        )

        return {
            "route": "hybrid",
            "intent": route["intent"],
            "structured_data": structured_result,
            "rag_data": rag_results,
        }

    return {
        "route": "unknown",
        "intent": None,
        "data": None,
    }
