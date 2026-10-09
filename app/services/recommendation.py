import re

from supabase import Client

from app.core.supabase import create_db_client
from app.services.offerings import (
    get_recommendation_candidates,
)


def normalize_text(text: str):
    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


STOPWORDS = {
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "a",
    "an",
    "the",
    "and",
    "or",
    "for",
    "to",
    "of",
    "on",
    "in",
    "with",
    "that",
    "this",
    "something",
    "need",
    "want",
    "would",
    "like",
    "can",
    "could",
    "do",
    "does",
    "how",
    "what",
    "which",
    "is",
    "are",
    "be",
    "myself",
    "please",
}


def normalize_term(term: str):
    """
    Normalize simple English word variations.

    This is intentionally lightweight.
    It is not a full NLP stemmer.
    """

    if len(term) <= 4:
        return term

    # -----------------------------------------------
    # Words ending in -ing
    # -----------------------------------------------

    if term.endswith("ing"):
        base = term[:-3]

        if len(base) >= 4:

            # capturing -> capture
            if base.endswith(("at", "it", "iv", "ur")):
                return base + "e"

            # answering -> answer
            return base

    # -----------------------------------------------
    # Words ending in -ed
    # -----------------------------------------------

    if term.endswith("ed"):
        base = term[:-2]

        if len(base) >= 4:

            # captured -> capture
            if base.endswith(("at", "it", "iv", "ur")):
                return base + "e"

            # answered -> answer
            return base

    return term


def extract_meaningful_terms(text: str):
    normalized = normalize_text(text)

    words = normalized.split()

    meaningful_words = [
        word
        for word in words
        if word not in STOPWORDS
    ]

    return [
        normalize_term(word)
        for word in meaningful_words
    ]


def get_offering_terms(offering: dict):
    name_terms = extract_meaningful_terms(
        offering.get("name", "")
    )

    alias_terms = []

    for alias in offering.get("aliases", []):
        alias_terms.extend(
            extract_meaningful_terms(alias)
        )

    description_terms = extract_meaningful_terms(
        offering.get("description", "")
    )

    return {
        "name": name_terms,
        "aliases": alias_terms,
        "description": description_terms,
    }


def score_offering(
    query: str,
    offering: dict,
):
    query_terms = set(
        extract_meaningful_terms(query)
    )

    offering_terms = get_offering_terms(
        offering
    )

    matched_terms = set()

    score = 0

    # -----------------------------------------------
    # Name matches
    # -----------------------------------------------

    for term in query_terms:

        if term in offering_terms["name"]:
            score += 15
            matched_terms.add(term)

    # -----------------------------------------------
    # Alias matches
    # -----------------------------------------------

    for term in query_terms:

        if term in offering_terms["aliases"]:
            score += 10
            matched_terms.add(term)

    # -----------------------------------------------
    # Description matches
    # -----------------------------------------------

    for term in query_terms:

        if term in offering_terms["description"]:
            score += 5
            matched_terms.add(term)

    return {
        "offering": offering["name"],
        "score": score,
        "matched_terms": sorted(matched_terms),
    }


def rank_offerings(
    query: str,
    offerings: list,
    minimum_score: int = 10,
):
    results = []

    # -----------------------------------------------
    # Score every offering
    # -----------------------------------------------

    for offering in offerings:

        result = score_offering(
            query=query,
            offering=offering,
        )

        results.append({
            "offering": offering,
            "score": result["score"],
            "matched_terms": result["matched_terms"],
        })

    # -----------------------------------------------
    # Highest score first
    # -----------------------------------------------

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # -----------------------------------------------
    # No candidates
    # -----------------------------------------------

    if not results:
        return []

    # -----------------------------------------------
    # No confident match
    # -----------------------------------------------

    if results[0]["score"] < minimum_score:
        return []

    # -----------------------------------------------
    # Keep ONLY confident recommendations
    # -----------------------------------------------

    results = [
        result
        for result in results
        if result["score"] >= minimum_score
    ]

    return results


def recommend_offerings(
    query: str,
    tenant_id: str,
    db: Client,
):
    offerings = get_recommendation_candidates(
        tenant_id=tenant_id,
        db=db,
    )

    return rank_offerings(
        query=query,
        offerings=offerings,
    )


if __name__ == "__main__":

    TENANT_ID = (
        "fc923830-3178-4cf8-98b2-23c2bc4e0015"
    )

    db = create_db_client()

    queries = [
        (
            "I need something that can answer customer "
            "questions on my website and capture leads."
        ),
        "I need accounting software.",
        "I need a website assistant.",
        "I need something that can capture leads.",
    ]

    print("\nLOADING REAL SUPABASE OFFERINGS...")

    offerings = get_recommendation_candidates(
        tenant_id=TENANT_ID,
        db=db,
    )

    print(
        f"\nFound {len(offerings)} offering(s)."
    )

    for offering in offerings:

        print("\n---")
        print("Name:", offering["name"])
        print("Type:", offering["type"])
        print("Price:", offering["price"])
        print("Currency:", offering["currency"])
        print("Available:", offering["available"])
        print("Image URL:", offering["image_url"])
        print("Aliases:", offering["aliases"])

    for query in queries:

        results = recommend_offerings(
            query=query,
            tenant_id=TENANT_ID,
            db=db,
        )

        print("\n==============================")
        print("QUERY:")
        print(query)

        if not results:

            print(
                "\nRecommendation: "
                "No confident match."
            )

            continue

        print("\nRECOMMENDATIONS:")

        for index, result in enumerate(
            results,
            start=1,
        ):

            offering = result["offering"]

            print("\n---")
            print("Rank:", index)
            print("Name:", offering["name"])
            print("Score:", result["score"])
            print(
                "Matched terms:",
                result["matched_terms"],
            )
            print("Price:", offering["price"])
            print("Currency:", offering["currency"])
            print("Available:", offering["available"])
            print(
                "Image URL:",
                offering["image_url"],
            )