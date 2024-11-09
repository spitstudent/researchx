from fastapi import FastAPI, Depends, Request, HTTPException, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # Import StaticFiles
from sqlalchemy.orm import Session
from routers import auth
from database import get_db, engine
import models, schemas
from sqlalchemy.exc import IntegrityError
import shutil
import os
from schemas import RecentItem
from typing import List
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import oauth2
from routers import paper, mashup, scraping_router

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",  # React frontend URL
    "http://localhost:8000",  # Add any other URLs you want to allow
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

templates = Jinja2Templates(directory='app/templates')
app.include_router(auth.router)
app.include_router(paper.router)
app.include_router(mashup.router)
app.include_router(scraping_router.router)
# Mount the static files directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get('/')
def root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})




@app.get("/recent", response_model=List[schemas.RecentItem])
def read_recent_papers(db: Session = Depends(get_db)):
    papers = db.query(models.ResearchPaper).all()
    return [schemas.RecentItem(
        id=paper.id,
        title=paper.title,
        category=paper.category,
        authors=paper.authors,
        description=paper.description,
        document_url=paper.document_url,
        created_at=paper.created_at.isoformat()  # Convert to ISO 8601 string
    ) for paper in papers]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)