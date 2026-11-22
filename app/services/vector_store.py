import faiss
import numpy as np
import os
import pickle

VECTOR_DIR = "vector_db"

class VectorStore:
    def __init__(self, dim=384):
        self.dim = dim
        os.makedirs(VECTOR_DIR,exist_ok = True)


    def _index_path(self, doc_id):
        return f"{VECTOR_DIR}/doc_{doc_id}.index"
    
    def _meta_path(self, doc_id):
        return f"{VECTOR_DIR}/doc_{doc_id}.pkl"
    
    #------------------------
    # SAVE Embedding    
    #------------------------

    def save(self, doc_id: int, embeddings, texts):
        index = faiss.IndexFlatL2(self.dim)
        vectors = np.array(embeddings).astype("float32")
        index.add(vectors)

        faiss.write_index(index, self._index_path(doc_id))
        clear_text = [str(t) for t in texts]

        with open(self._meta_path(doc_id),"wb") as f:
            pickle.dump(clear_text,f)

    
    #-------------------------
    #  SEARCH
    #-------------------------

    def search(self, doc_id: int,   query_embedding,top_k = 5):
        idx_path = self._index_path(doc_id)
        meta_path = self._meta_path(doc_id)

        if not os.path.exists(idx_path) or not os.path.exists(meta_path):
            return []

        index = faiss.read_index(idx_path)

        with open(meta_path,"rb") as f:
            texts = pickle.load(f)

        if not texts:
            return []

        query_vector = np.array([query_embedding]).astype("float32")

        actual_k = min(top_k, len(texts))
        distances, indices = index.search(query_vector, actual_k)

        results = [str(texts[i]) for i in indices[0] if 0 <= i < len(texts)]
        return results


