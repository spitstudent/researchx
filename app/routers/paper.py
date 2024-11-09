from fastapi import  Depends, HTTPException, UploadFile, File, Form, APIRouter,Query
from fastapi.responses import JSONResponse
import schemas, models, oauth2
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List,Optional
import shutil
import os
from database import get_db

router = APIRouter()

@router.post('/submit')
async def submit_paper(
    title: str = Form(...),
    category: str = Form(...),
    authors: str = Form(...),
    description: str = Form(...),
    document: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)  # Get current user from token
):
    # Save the uploaded file
    document_filename = document.filename
    document_path = f"static/{document_filename}"
    
    with open(document_path, "wb") as buffer:
        shutil.copyfileobj(document.file, buffer)
    
    # Create a new research paper record
    try:
        new_paper = models.ResearchPaper(
            title=title,
            category=category,
            authors=authors,
            description=description,
            document_url=f"static/{document_filename}"  # Update URL to reflect static path
        )
        db.add(new_paper)
        db.commit()
        return {"message": "Research paper submitted successfully!"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error in submitting paper")
    
@router.delete("/delete/{paper_id}")
def delete_paper(
    paper_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    paper = db.query(models.ResearchPaper).filter(models.ResearchPaper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(404, detail="Paper not found")
    
    print(f"Current user: {current_user.user_name}, Paper author: {paper.authors}")  # log  for debugging
    # Try to delete the associated file from the filesystem
    document_path = paper.document_url
    if os.path.exists(document_path):
        os.remove(document_path)  # Delete the file from the filesystem
    
    db.delete(paper)
    db.commit()
    
    return {"message": "Research paper deleted successfully!"}

@router.put('/modifypaper/{id}', response_class=JSONResponse)
async def modifyer(
    id: int,
    title: str = Form(...),
    category: str = Form(...),
    authors: str = Form(...),
    description: str = Form(...),
    document: UploadFile = File(None),  # Make document optional
    db: Session = Depends(get_db)
):
    paper_query = db.query(models.ResearchPaper).filter(models.ResearchPaper.id == id)
    paper = paper_query.first()
    
    if paper is None:
        raise HTTPException(404, detail="Paper not found")

    # Update fields
    paper.title = title
    paper.category = category
    paper.authors = authors
    paper.description = description

    if document:  # If a new document is uploaded
        # Save the uploaded file
        document_filename = document.filename
        document_path = f"static/{document_filename}"
        
        with open(document_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)
        
        paper.document_url = f"static/{document_filename}"

    db.commit()
    return {"data": "Successfully modified paper"}


        
@router.get('/findpaper')
async def paper_finder(author: Optional[str] = Query(None),
                       title: Optional[str] = Query(None),
                       category: Optional[str] = Query(None),
                       db: Session = Depends(get_db)
                       ):
    papers_query = db.query(models.ResearchPaper)

    if author:
        papers_query = papers_query.filter(models.ResearchPaper.authors.ilike(f"%{author}%"))  # Partial match for author

    if category:
        category = category.lower()
        papers_query = papers_query.filter(models.ResearchPaper.category.ilike(f"%{category}%"))  # Case-insensitive partial match

    if title:
        papers_query = papers_query.filter(models.ResearchPaper.title.ilike(f"%{title}%"))  # Partial match for title

    papers = papers_query.all()
    return {"papers": papers}



@router.get('/paper/{id}', response_class=JSONResponse)
async def individual_paper(id:int , db:Session = Depends(get_db)):
    """ Use this endpoint for individual paper details based on ID that should be sent via front-end
    """
    individual_paper = db.query(models.ResearchPaper).filter(models.ResearchPaper.id == id).first()
    if individual_paper == None:
        raise HTTPException(404, detail = "Paper Not found")
    return {'paper':individual_paper}
        
    
@router.get("/recent", response_model=List[schemas.RecentItem])
async def read_recent_papers(db: Session = Depends(get_db)):
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
