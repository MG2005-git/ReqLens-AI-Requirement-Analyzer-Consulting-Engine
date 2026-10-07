from fastapi import FastAPI , UploadFile , File , HTTPException
from app.services.parser import analyze_file
from datetime import datetime
from app.services.ai_agent import analyze_requirements_with_ai
from app.api.auth_routes import router as auth_router
from app.api.documents import router as documents_router
from app.database import engine
from app import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(documents_router)
@app.get("/")
def health_check():
    return {"status" : "ok"}

@app.post("/analyze")
async def analyze_doc( file: UploadFile = File(...)):

    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail = "Only .txt files are supported")
    

    
    

    content = await file.read()

    try:
        text = content.decode("utf-8").strip()
    except UnicodeDecodeError:
        raise HTTPException(
            status_code = 400,
            detail = "File must be UTF-8 encoded text"
        )

    if not text:
        raise HTTPException(status_code = 400, detail = "Upload file is empty" )  


    basic_analysis = analyze_file(text)
    ai_analysis = analyze_requirements_with_ai(text)

    result  = {
        **basic_analysis,
        **ai_analysis 
    }
    return {
        "agent": "ArchReq-AI",
        "version" : "0.1",
        "status" : "success",
      #  "timestamp" : datetime.utcnow().isoformat,
        "data" :  result
    }