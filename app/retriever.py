"""Per-clause-type retrieval from Supabase pgvector.

Each segmented clause is matched only against rules tagged with its own
clause_category (via the match_rules SQL function) — never a global search.
"""

from app.config import get_embeddings, get_supabase
from app.schemas import ClauseCategory


def retrieve_rules(clause_text: str, category: ClauseCategory,
                   match_count: int = 4) -> list[dict]:
    """Return the most relevant rules for a clause, category-filtered."""
    embedding = get_embeddings().embed_query(clause_text)
    resp = get_supabase().rpc(
        "match_rules",
        {
            "query_embedding": embedding,
            "category": category.value,
            "match_count": match_count,
        },
    ).execute()
    return resp.data
