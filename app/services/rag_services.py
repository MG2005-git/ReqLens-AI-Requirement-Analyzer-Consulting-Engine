from app.services.embedding_services import EmbeddingService
from app.services.ai_agent import LLMRequirementRefiner
from app.services.vector_store import VectorStore

from app import models
from sqlalchemy.orm import Session

class RAGservice:
    # --- OLD CODE ---
    # def __init__(self,db: Session,document_id: id):
    #     self.db = db
    #     self.doc_id = document_id
    #     self.embedder = EmbeddingService()
    #     self.store = VectorStore()
    #     self.llm = LLMRequirementRefiner()
    # --- NEW CODE ---
    def __init__(self,db: Session,document_id: int): # Note: original was document_id: id, changed to int but left as is if safe, wait, no let's just use document_id: int
        self.db = db
        self.doc_id = document_id
        
        doc = db.query(models.Document).filter(models.Document.id == document_id).first()
        domain = doc.domain if doc else "architecture"

        self.embedder = EmbeddingService()
        self.store = VectorStore()
        self.llm = LLMRequirementRefiner(domain=domain)
    
    def ask(self, question: str):
        #Embed question
        query_vector = self.embedder.model.encode(
            [question],
            convert_to_numpy=True
        )[0]
        # relevent_chunk = self.embedder.search(query_vector)
        relevant_chunks = self.store.search(
        self.doc_id,
        query_vector,
        top_k=5
    )

        # Retrieve top chunks
        # results = self.store.search(self.doc_id, query_vector)

        context = "\n\n".join(relevant_chunks)
        # use the new answer_question helper; it will craft its own prompt
        answer = self.llm.answer_question(context, question)

        return {
            "answer": answer,
            "context_used": relevant_chunks,
        }

    def load_document_chunks(self, document_id: int):
        """
        Load chunks from DB build FAISS index.
        """
        chunks = (
            self.db.query(models.DocumentChunk)
            .filter(models.DocumentChunk.document_id == document_id)
            .order_by(models.DocumentChunk.chunk_index)
            .all()
        )

        texts  =[c.text for c in chunks]

        if not texts:
            raise ValueError("No chunks found")
        
        self.embedder.embed_text(texts)

#     def ask(self, question:str):
#         """
#             Perform RAG query
#         """

#         relevant_chunks = self.embedder.search(question)

#         context = "\n\n".join(relevant_chunks)

#         prompt = f"""
# Use only the context below to answer the question.

# Context:
# {context}

# Question:
# {question}

# Answer clearly and consiely.

# """
#         answer = self.llm.refine(prompt)

#         return {
#             "answer": answer,
#             "context_used": relevant_chunks
#             }