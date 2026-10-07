from app.services.embedding_services import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.ai_agent import DocumentAI, LLMRequirementRefiner

from app import models
from sqlalchemy.orm import Session

from app.utils.chunkers import chunk_text

import json

def process_document_async(db: Session,document_id: int):
    """
        Background worker to process document fully.
        Run after upload.
    """


    document = db.query(models.Document).get(document_id)

    try:
        document.status = models.ProcessingStatus.processing
        db.commit()
       

        #---------------------------
        # GET TEXT FROM DB
        #---------------------------

        doc_text = db.query(models.DocumentText).filter(models.DocumentText.document_id == document_id).first()

        if not doc_text:
            raise ValueError("No document text found")
        
        full_text = doc_text.text

        #---------------------------
        # CHUNK TEST
        #---------------------------
        print("start of chunk_test")

        chunks = chunk_text(full_text)
        # Ensure chunks are plain strings
        chunk_texts = [c[1] if isinstance(c, tuple) else c for c in chunks]
        print("end of chunk test")

        # save chunks in DB
        for idx, chunk in enumerate(chunk_texts):
            db.add(models.DocumentChunk(
                document_id = document_id,
                chunk_index = idx,
                text = str(chunk)
            ))
        db.commit()

        #--------------------
        # CREATE EMBEDDINGS
        #--------------------

        embedder = EmbeddingService()
        vectors = embedder.embed_text(chunk_texts)

        store = VectorStore()
        store.save(document_id, vectors, chunk_texts)

        #-------------------------
        # EXTRACTED STRUCTURED DATA
        #--------------------------

        # --- OLD CODE ---
        # ai = DocumentAI()
        # structured = ai.analyze_document(full_text)
        # 
        # #--------------------------
        # # CLEAN REQUIREMENTS USING LLM
        # #--------------------------
        # 
        # refiner = LLMRequirementRefiner()
        # clean_text = refiner.refine(full_text)
        # 
        # document.extracted_data = structured
        # document.clean_requirements = clean_text
        # --- NEW CODE ---
        ai = DocumentAI(domain=document.domain)
        result = ai.analyze_document(full_text)

        
        document.extracted_data = result["structured_data"]
        document.clean_requirements = result["refine_text"]
        document.status = models.ProcessingStatus.processed

        db.commit()

    except Exception as e:
        print("Real error:",e)
        document.status = models.ProcessingStatus.failed
        document.error_message = str(e)
        db.commit()