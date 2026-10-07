# --- OLD CODE ---
# from fastapi import APIRouter, Depends , UploadFile , File , HTTPException, BackgroundTasks
# --- NEW CODE ---
from fastapi import APIRouter, Depends , UploadFile , File , HTTPException, BackgroundTasks, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
from app.schemas import DocumentResponse
from app.utils.files import validate_file, extract_text
from app.models import DocumentText
from app.utils.text import normalize_text
from app.utils.pdf import extract_text_from_pdf
from app.models import ProcessingStatus
from app.utils.chunkers import chunk_text
from app.models import DocumentChunk
from fastapi.responses import FileResponse

from app.services.embedding_services import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.rag_services import  RAGservice
from app.services.pdf_generator import generate_requirements_pdf
from app.services.ai_agent import DocumentAI
from app.services.requirement_extractor import extract_requirements
from app.services.background_task import process_document_async

import json

router = APIRouter(
    prefix="/documents",
    tags= ["Documents"]
)
# #--------------Upload route ------------------
# @router.post("/upload", response_model=DocumentResponse)
# async def upload_document(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     validate_file(file)
#     file_bytes = await file.read()

#     #content = await extract_text(file)

#     document = models.Document(
#         filename = file.filename,
#         user_id = current_user.id,
#         status = ProcessingStatus.uploaded
#     )
   
#     db.add(document)
#     db.commit()
#     db.refresh(document)

#     try:
       
#         document.status = ProcessingStatus.processing
#         db.commit()

#         if file.filename.lower().endswith(".pdf"):
#             raw_text = extract_text_from_pdf(file_bytes)
#         else:
#             raw_text = file_bytes.decode("utf-8")
        

#         if not raw_text.strip():
#             raise ValueError("No extractable text found")
        
#         normalized = normalize_text(raw_text)
#         document_text = DocumentText(
#             text = normalized,
#             document_id = document.id
#         )

#         db.add(document_text)
#         document.status = ProcessingStatus.processing
#         db.commit()
#         db.refresh(document_text)
        
#         chunks = chunk_text(normalized)
#         chunk_texts = []
        

#         for idx, chunk in enumerate(chunks):
#             db.add(DocumentChunk(
#                 document_id = document.id,
#                 chunk_index = idx,
#                 text = chunk
#             ))
           
#             chunk_texts.append(chunk)

#         db.commit()
#         document.status = ProcessingStatus.processing
#         db.commit()

#         #---------------------------
#         # CREATE EMBEDDINGS + STORE IN FAISS
#         #---------------------------
        

#         embedder = EmbeddingService()
       
#         vectors = embedder.model.encode(
#             chunk_texts,
#             convert_to_numpy=True
#             ).astype("float32")
        
#         print("Before for vectors",vectors)
#         store = VectorStore()
#         store.save(document.id, vectors,chunk_texts)

#         # all_chunks = db.query(models.DocumentChunk).filter(
#         #     models.DocumentChunk.document_id == document.id
#         # ).order_by(models.DocumentChunk.chunk_index).all()

#         # full_text    = " ".join(chunk.text for chunk in all_chunks)

#         # #Extract structured requirements

#         # structured_data = extract_requirements(full_text)

#         # #save JSON  into document
#         # document.extracted_data = structured_data

#         #db.commit()



#     except Exception as e:
#         print("🔥 REAL ERROR:", repr(e))
#         document.status = ProcessingStatus.failed
#         document.error_message = str(e)
#         db.commit()

#         raise HTTPException(
#             status_code = 400,
#             detail = "Document Processing Failed"
#         )

#     return document




#--------------Upload route ------------------
@router.post("/upload", response_model=DocumentResponse)
# --- OLD CODE ---
# async def upload_document(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
# --- NEW CODE ---
async def upload_document(
    background_tasks : BackgroundTasks,
    file: UploadFile = File(...),
    domain: str = Form("architecture"),

    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    validate_file(file)
    file_bytes = await file.read()

    #content = await extract_text(file)

    # --- OLD CODE ---
    # document = models.Document(
    #     filename = file.filename,
    #     user_id = current_user.id,
    #     status = ProcessingStatus.uploaded
    # )
    # --- NEW CODE ---
    document = models.Document(
        filename = file.filename,
        user_id = current_user.id,
        status = ProcessingStatus.uploaded,
        domain = domain
    )
   
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
       
        document.status = ProcessingStatus.processing
        db.commit()

        if file.filename.lower().endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8")
        

        if not raw_text.strip():
            raise ValueError("No extractable text found")
        
        normalized = normalize_text(raw_text)
        document_text = DocumentText(
            text = normalized,
            document_id = document.id
        )

        db.add(document_text)
        document.status = ProcessingStatus.processing
        db.commit()
        db.refresh(document_text)
        
        background_tasks.add_task(
            process_document_async,
            db,
            document.id
        )

        return document

        # all_chunks = db.query(models.DocumentChunk).filter(
        #     models.DocumentChunk.document_id == document.id
        # ).order_by(models.DocumentChunk.chunk_index).all()

        # full_text    = " ".join(chunk.text for chunk in all_chunks)

        # #Extract structured requirements

        # structured_data = extract_requirements(full_text)

        # #save JSON  into document
        # document.extracted_data = structured_data

        # db.commit()




    except Exception as e:
        print("🔥 REAL ERROR:", repr(e))
        document.status = ProcessingStatus.failed
        document.error_message = str(e)
        db.commit()

        raise HTTPException(
            status_code = 400,
            detail = "Document Processing Failed"
        )

@router.post("/{document_id}/analyze")
def analyze_document(
    document_id : int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch document and validate ownership
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="document not found")
    
    if document.status == ProcessingStatus.processed:
        raise HTTPException(
            status_code=400,
            detail="Document already analyzed"
        )
    print(document.status)
    if document.status != ProcessingStatus.processing:
        raise HTTPException(
            status_code= 400,
            detail="Document not ready for analysis"
        )
       
    
    document.status = ProcessingStatus.processing
    db.commit()

    try:
        #fetch chunks
        chunks = db.query(models.DocumentChunk).filter(
            models.DocumentChunk.document_id == document.id
        ).order_by(models.DocumentChunk.chunk_index).all()

        if not chunks:
            raise ValueError("No chunks found for document")
        
        # Merge chunks 
        full_text = " ".join(chunk.text for chunk in chunks)

        # # Run extraction engine
        # structured_data = extract_requirements(full_text)

        # document.extracted_data = structured_data
        # document.status = ProcessingStatus.processed
        # db.commit()
        print(full_text)

        # AI LAYER CALL
        # --- OLD CODE ---
        # ai = DocumentAI()
        # --- NEW CODE ---
        ai = DocumentAI(domain=document.domain)
        result = ai.analyze_document(full_text)
        

        # save the dict directly; the Column(JSON) will handle serialization
        document.extracted_data = result["structured_data"]
        document.clean_requirements = result["refine_text"]
        document.analysis_result = result
        document.status = ProcessingStatus.processed
        db.commit()

        # expose the entire result (includes structured_data and refine_text)
        return {
            "status": "processed",
            "document_id": document.id,
            "analysis": result,
            "extracted_data": result["structured_data"],
            "clean_requirements": result["refine_text"]
        }
    except Exception as e:
        print("🔥 REAL ERROR:", repr(e))
        document.status = ProcessingStatus.failed   
        document.error_message = str(e)
        db.commit() 

        raise HTTPException(
            status_code= 400,
            detail="Document processing failed"
        )


@router.get("/{document_id}/download")
def download_document(
    document_id : int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    document =  db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.clean_requirements:
        raise HTTPException(status_code=404, detail="Document not analyzed yet")
    

    file_path = generate_requirements_pdf(
        document.id,
        document.clean_requirements,
        analysis=document.analysis_result,
    )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=f"requirements_{document.id}.pdf"
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="document not found")
    # older entries may have extracted_data stored as a JSON string; convert
    if isinstance(document.extracted_data, str):
        try:
            document.extracted_data = json.loads(document.extracted_data)
        except Exception:
            # leave it as-is; response validation will catch it if still wrong
            pass
    return document


@router.post("/{document_id}/ask")
def ask_document(
    document_id: int,
    question: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
        ).first()
    
    if not document:
        raise HTTPException(404,"Document not found")
    
    rag  = RAGservice(db, document_id)

    rag.load_document_chunks(document_id)

    result = rag.ask(question)

    return result

