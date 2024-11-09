from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    email = Column(String(length=255), unique=True, index=True)
    password = Column(String(length=255))
    name = Column(String(length=255))

class ResearchPaper(Base):
    __tablename__ = 'research_papers'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String)
    authors = Column(String)
    description = Column(Text)
    document_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class FetchedQuery(Base):
    __tablename__ = 'fetched_queries'
    id = Column(Integer, primary_key=True)
    query_text = Column(String, unique=True)
    timestamp = Column(String)  # Use appropriate date-time type if available
    papers = relationship("FetchedPaper", back_populates="query")

class FetchedPaper(Base):
    __tablename__ = 'fetched_papers'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('fetched_queries.id'))
    title = Column(String)
    summary = Column(String)
    authors = Column(String)  # You may store as JSON or separate table if needed
    pdf_link = Column(String)
    query = relationship("FetchedQuery", back_populates="papers")

    # Unique constraint to prevent duplicate entries based on title and pdf_link
    __table_args__ = (UniqueConstraint('title', 'pdf_link', name='_title_pdf_uc'),)
    
class PaperStats(Base): 
    __tablename__ = 'paper_stats'
    
    id = Column(Integer, primary_key=True, index=True)  
    paper_id = Column(Integer, ForeignKey('research_papers.id'), index=True)  
    citation_count = Column(Integer)

