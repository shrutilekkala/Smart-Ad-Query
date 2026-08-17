from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..rag import answer_question, retrieve
from ..schemas import RagRequest, RagResponse, SearchResponse

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
def semantic_search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    results = retrieve(db, q, top_k=top_k)
    return {"query": q, "results": results}


@router.post("/query", response_model=RagResponse)
def rag_query(payload: RagRequest, db: Session = Depends(get_db)):
    result = answer_question(db, payload.question, top_k=payload.top_k)
    return {
        "question": payload.question,
        "answer": result["answer"],
        "sources": result["sources"],
        "generated_by": result["generated_by"],
    }
