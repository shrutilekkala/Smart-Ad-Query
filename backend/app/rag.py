"""Retrieval-augmented generation over the ad corpus.

Retrieval always runs through FAISS. Generation uses the Anthropic API when
ANTHROPIC_API_KEY is configured; otherwise it falls back to a deterministic
extractive summary built from the retrieved records, so the endpoint is
fully functional (and testable) with zero external dependencies.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from .config import ANTHROPIC_API_KEY
from .metrics import ad_to_metrics_dict
from .models import Ad
from .vector_store import get_vector_store


def retrieve(db: Session, question: str, top_k: int = 5) -> list[dict]:
    store = get_vector_store()
    hits = store.search(question, top_k=top_k)
    results = []
    for ad_id, score in hits:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad is None:
            continue
        results.append({"ad": ad_to_metrics_dict(ad), "score": round(score, 4)})
    return results


def _build_context(sources: list[dict]) -> str:
    lines = []
    for s in sources:
        ad = s["ad"]
        lines.append(
            f"- [{ad['campaign_name']} / {ad['platform']}] \"{ad['ad_copy']}\" "
            f"(CTR={ad['ctr']:.2%}, CPC=${ad['cpc']:.2f}, ROAS={ad['roas']:.2f}x, "
            f"spend=${ad['spend']:.2f}, revenue=${ad['revenue']:.2f})"
        )
    return "\n".join(lines)


def _extractive_answer(question: str, sources: list[dict]) -> str:
    if not sources:
        return "No matching ads were found for that query."
    best = max(sources, key=lambda s: s["ad"]["roas"])
    top_names = ", ".join(sorted({s["ad"]["campaign_name"] for s in sources}))
    return (
        f"Based on the {len(sources)} most relevant ads for \"{question}\", "
        f"the top-performing match is \"{best['ad']['campaign_name']}\" on "
        f"{best['ad']['platform']} with a CTR of {best['ad']['ctr']:.2%} and "
        f"ROAS of {best['ad']['roas']:.2f}x. Related campaigns retrieved: {top_names}."
    )


def _llm_answer(question: str, sources: list[dict]) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    context = _build_context(sources)
    prompt = (
        "You are an ad-analytics assistant. Answer the question using ONLY the "
        "ad records below. Cite campaign names and metrics in your answer.\n\n"
        f"Ad records:\n{context}\n\nQuestion: {question}"
    )
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if hasattr(block, "text"))


def answer_question(db: Session, question: str, top_k: int = 5) -> dict:
    sources = retrieve(db, question, top_k=top_k)

    if ANTHROPIC_API_KEY:
        try:
            answer = _llm_answer(question, sources)
            return {"answer": answer, "sources": sources, "generated_by": "llm"}
        except Exception:
            pass  # fall through to extractive answer if the LLM call fails

    answer = _extractive_answer(question, sources)
    return {"answer": answer, "sources": sources, "generated_by": "extractive"}
