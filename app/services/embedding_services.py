from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.chunk_texts = []

    # def build_index(self,chunks: list[str]):
    #     """
    #     Create  FAISS index from document chunks.
    #     """
    #     self.chunk_texts = chunks

    #     embedding = self.model.encode(chunks, convert_to_numpy=True)
    #     dimension = embedding.shape[1]

    #     self.index = faiss.IndexFlatL2(dimension)
    #     self.index.add(embedding)

    def embed_text(self,texts: list[str]) -> np.ndarray:
        """
        convert list of text into embeddings
        """
        if not texts:
            raise ValueError("No text provided for embedding")
        
        embeddings = self.model.encode(texts,convert_to_numpy=True)
        return embeddings

    
    # def search(self,query: str,top_k: int = 3):
    def search(self,query: str) -> np.ndarray :
        """
        Search most relevent chunks.
        """
        embedding = self.model.encode([query], convert_to_numpy= True)
        return embedding[0]
        # if not self.index:
        #     raise ValueError("Index not built")
        
        # query_embedding = self.model.encode([query],convert_to_numpy = True)
        # distances ,  indices = self.index.search(query_embedding, top_k)
        # result = [self.chunk_texts[i] for i in indices[0]]
        # return result

