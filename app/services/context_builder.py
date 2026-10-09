
def build_context(
    structured_data=None,
    rag_results=None,
):
    """
    Build context for the LLM.

    Structured database records are authoritative for
    business facts. RAG provides relevant business knowledge.
    """

    context_parts = []

    # --------------------------------------------------
    # Structured business data
    # --------------------------------------------------

    if structured_data is not None:

        # Recommendation results
        if isinstance(structured_data, list):

            if structured_data and all(
                isinstance(item, dict) and "offering" in item
                for item in structured_data
            ):
                recommendation_parts = []

                for index, result in enumerate(
                    structured_data,
                    start=1,
                ):
                    offering = result.get("offering") or {}

                    recommendation_parts.append(
                        f"RECOMMENDATION {index}:\n"
                        f"Name: {offering.get('name')}\n"
                        f"Type: {offering.get('type')}\n"
                        f"Description: {offering.get('description')}\n"
                        f"Price: {offering.get('price')} "
                        f"{offering.get('currency')}\n"
                        f"Available: {offering.get('available')}\n"
                        f"Quantity: {offering.get('quantity')}\n"
                        f"SKU: {offering.get('sku')}\n"
                        f"Image URL: {offering.get('image_url')}\n"
                        f"Recommendation Score: {result.get('score')}\n"
                        f"Matched Terms: {', '.join(result.get('matched_terms') or [])}"
                    )

                if recommendation_parts:
                    context_parts.append(
                        "RECOMMENDATION DATA:\n"
                        + "\n\n".join(recommendation_parts)
                    )

            else:
                # Ordinary catalog records returned by get_products()
                catalog_parts = []

                for index, offering in enumerate(
                    structured_data,
                    start=1,
                ):
                    if not isinstance(offering, dict):
                        continue

                    product_details = offering.get("product_details")

                    if isinstance(product_details, list):
                        product_details = (
                            product_details[0]
                            if product_details
                            else {}
                        )

                    product_details = product_details or {}

                    catalog_parts.append(
                        f"CATALOG ITEM {index}:\n"
                        f"ID: {offering.get('id')}\n"
                        f"Name: {offering.get('name')}\n"
                        f"Type: {offering.get('type')}\n"
                        f"Description: {offering.get('description')}\n"
                        f"Price: {offering.get('price')} "
                        f"{offering.get('currency')}\n"
                        f"Available: {offering.get('available')}\n"
                        f"Quantity: {offering.get('quantity', product_details.get('quantity'))}\n"
                        f"SKU: {offering.get('sku', product_details.get('sku'))}\n"
                        f"Image URL: {offering.get('image_url')}"
                    )

                if catalog_parts:
                    context_parts.append(
                        "PRODUCT CATALOG DATA:\n"
                        + "\n\n".join(catalog_parts)
                    )

        # Single structured result
        elif isinstance(structured_data, dict):

            offering = structured_data.get("offering")

            if offering:
                context_parts.append(
                    "STRUCTURED OFFERING DATA:\n"
                    f"{offering}"
                )

            # Include authoritative details for the requested intent.
            for key in (
                "price_details",
                "availability_details",
                "quantity_details",
                "description_details",
            ):
                details = structured_data.get(key)

                if details is not None:
                    context_parts.append(
                        f"{key.upper()}:\n{details}"
                    )

            # Handle existing structured responses such as product counts
            # and any legacy dictionary-shaped result.
            if not offering and not any(
                key in structured_data
                for key in (
                    "price_details",
                    "availability_details",
                    "quantity_details",
                    "description_details",
                )
            ):
                context_parts.append(
                    "STRUCTURED BUSINESS DATA:\n"
                    f"{structured_data}"
                )

    # --------------------------------------------------
    # RAG knowledge
    # --------------------------------------------------

    if rag_results:

        knowledge_parts = []

        for result in rag_results:
            if not isinstance(result, dict):
                continue

            content = result.get("content")

            if content:
                knowledge_parts.append(content)

        if knowledge_parts:
            context_parts.append(
                "BUSINESS KNOWLEDGE:\n"
                + "\n\n".join(knowledge_parts)
            )

    # --------------------------------------------------
    # Final context
    # --------------------------------------------------

    if not context_parts:
        return None

    return "\n\n".join(context_parts)
