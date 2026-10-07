from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Enum
import enum
from app.database import Base
from sqlalchemy import JSON
from sqlalchemy.sql import func


class ProcessingStatus(enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
#    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ProcessingStatus), default = ProcessingStatus.uploaded, nullable = False)
    
    # --- OLD CODE ---
    # error_message = Column(Text, nullable=True)
    # extracted_data = Column(JSON, nullable=True)
    # clean_requirements = Column(Text, nullable=True)
    # --- NEW CODE ---
    domain = Column(String, default="architecture", nullable=False)
    error_message = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    clean_requirements = Column(Text, nullable=True)
    # full JSON result returned by LLM analysis (structured + metadata)
    analysis_result = Column(JSON, nullable=True)


    user = relationship("User", back_populates="documents")
   # analysis = relationship("Analysis", back_populates="document", uselist=False)
    text = relationship(
        "DocumentText",
        back_populates="document",
        uselist=False,
        cascade="all, delete"
    )


# class Analysis(Base):
#     __tablename__ = "analyses"

#     id = Column(Integer, primary_key=True, index=True)
#     document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
#     analysis_json = Column(Text, nullable=False)
#     pdf_path = Column(String, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     document = relationship("Document", back_populates="analysis")


class DocumentText(Base):
    __tablename__ = "document_texts"

    id = Column(Integer, primary_key = True , index = True)
    text = Column(Text, nullable = False)


    document_id = Column(Integer , ForeignKey("documents.id"),nullable=False)

    document = relationship("Document", back_populates="text")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer,primary_key=True,index = True)
    document_id = Column(Integer,ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable = False )
    text = Column(Text,nullable=False)

    document = relationship("Document")







