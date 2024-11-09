from fastapi import Depends, HTTPException, APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import models
import schemas
from database import get_db
from models import FetchedQuery, FetchedPaper  # Ensure models are correctly defined
from scraping import scraping_util  # Assuming `scraping_util` contains `fetch_arxiv_papers`
from sqlalchemy.exc import IntegrityError

router = APIRouter()

def save_query_and_papers(session: Session, query_text: str, papers: list):
    # Check if the query already exists to avoid duplication
    query = session.query(FetchedQuery).filter_by(query_text=query_text).first()
    if not query:
        query = FetchedQuery(query_text=query_text, timestamp=str(datetime.now()))
        session.add(query)
        session.commit()

    # Insert papers, checking for uniqueness based on title and pdf_link
    saved_papers = []
    for paper_data in papers:
        paper = FetchedPaper(
            query_id=query.id,
            title=paper_data["title"],
            summary=paper_data["summary"],
            authors=json.dumps(paper_data["authors"]),
            pdf_link=paper_data["pdf_link"]
        )
        try:
            session.add(paper)
            session.commit()
            saved_papers.append(paper)  # Add to saved list if successfully committed
        except IntegrityError:
            session.rollback()  # Skip duplicates if they exist

    return saved_papers


@router.post('/fetch_internet')
async def net_fetch(query: Optional[str] = Query(None), max_results: Optional[int] = Query(20), db: Session = Depends(get_db)):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required.")
    
    # Fetch papers from arXiv
    papers = scraping_util.fetch_arxiv_papers(query, max_results=max_results)
    
    # Save to database and get saved papers
    saved_papers = save_query_and_papers(db, query, papers)
    
    # Format response
    response_data = [
        {
            "title": paper.title,
            "summary": paper.summary,
            "authors": json.loads(paper.authors),
            "pdf_link": paper.pdf_link
        } for paper in saved_papers
    ]

    return JSONResponse(content={"query": query, "results": response_data})

@router.post('/citation_counts')
async def citation_count(paper: schemas.ResearchPaper, db:Session = Depends(get_db)):
    db_query = db.query(models.PaperStats).filter(models.PaperStats.paper_id == paper.id).first()
    if db_query != None:
        return db_query.citation_count
    num_citations = scraping_util.get_google_scholar_citations(paper.title)
    paper_stats = models.PaperStats(paper_id = paper.id, citation_count = num_citations)
    db.add(paper_stats)
    db.commit()
    db.refresh(paper_stats)
    return paper_stats.citation_count
    

@router.post('/fetch_related')
async def related_fetch(query: schemas.Fetch):
    response = scraping_util.fetch_related_papers(query=query.query)
    return response