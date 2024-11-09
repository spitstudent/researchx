from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Login(BaseModel):
    email: str
    password: str

class NewUser(BaseModel):
    name: str
    username: str
    email: str
    password: str

class ResearchPaperBase(BaseModel):
    title: str
    category: str
    authors: str
    description: str
    document_url: str

class ResearchPaperCreate(ResearchPaperBase):
    pass

class ResearchPaper(ResearchPaperBase):
    id: int
    created_at: datetime  # Use datetime for consistency

    @classmethod
    def from_orm(cls, orm_obj):
        return cls(
            id=orm_obj.id,
            title=orm_obj.title,
            category=orm_obj.category,
            authors=orm_obj.authors,
            description=orm_obj.description,
            document_url=orm_obj.document_url,
            created_at=orm_obj.created_at
        )

    class Config:
        orm_mode = True  # Use orm_mode for better compatibility with SQLAlchemy

class RecentItem(BaseModel):
    id: int
    title: str
    category: str
    authors: str
    description: str
    document_url: Optional[str] = None  # Make it optional if not all papers have a URL
    created_at: str  # or datetime if you handle conversion elsewhere

class PDF_chat(BaseModel):
    query: str
    pdf_file: str
    
class TokenData(BaseModel):
    user_name: str
    user_role: str
class PDF_summarize(BaseModel):
    pdf_file:str
    
class Fetch(BaseModel):
    query: str
