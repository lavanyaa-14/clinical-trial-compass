import json
import os
import numpy as np
from pathlib import Path


class VectorStore:
    """Simple file-based vector store with numpy similarity search"""
    
    def __init__(self, path: str = "./chroma_db"):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        
        self.embeddings_file = self.path / "embeddings.npy"
        self.metadata_file = self.path / "metadata.json"
        self.ids_file = self.path / "ids.json"
        self.documents_file = self.path / "documents.json"
        
        # Load existing data
        self.embeddings = []
        self.metadata = []
        self.ids = []
        self.documents = []
        self._load()

    def _load(self):
        """Load data from disk if it exists"""
        try:
            if self.embeddings_file.exists():
                self.embeddings = np.load(self.embeddings_file, allow_pickle=False).tolist()
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            if self.ids_file.exists():
                with open(self.ids_file, 'r') as f:
                    self.ids = json.load(f)
            if self.documents_file.exists():
                with open(self.documents_file, 'r') as f:
                    self.documents = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing data: {e}")

    def _save(self):
        """Save data to disk"""
        np.save(self.embeddings_file, np.array(self.embeddings))
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f)
        with open(self.ids_file, 'w') as f:
            json.dump(self.ids, f)
        with open(self.documents_file, 'w') as f:
            json.dump(self.documents, f)

    def add_documents(self, documents: list[str], embeddings: list[list[float]], 
                      ids: list[str], metadatas: list[dict]):
        """Add documents and embeddings to the store"""
        self.embeddings.extend(embeddings)
        self.documents.extend(documents)
        self.ids.extend(ids)
        self.metadata.extend(metadatas)
        self._save()

    def query(self, embedding: list[float], n_results: int = 15) -> dict:
        """Query the store using cosine similarity"""
        if not self.embeddings:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        # Convert to numpy for similarity calculation
        query_vec = np.array(embedding)
        embeddings_array = np.array(self.embeddings)
        
        # Cosine similarity
        query_norm = np.linalg.norm(query_vec)
        embeddings_norm = np.linalg.norm(embeddings_array, axis=1)
        
        similarities = np.dot(embeddings_array, query_vec) / (embeddings_norm * query_norm + 1e-8)
        
        # Get top n_results
        top_indices = np.argsort(similarities)[::-1][:n_results]
        
        results = {
            "ids": [[self.ids[i] for i in top_indices]],
            "documents": [[self.documents[i] for i in top_indices]],
            "metadatas": [[self.metadata[i] for i in top_indices]],
            "distances": [[float(1 - similarities[i]) for i in top_indices]]
        }
        
        return results

    def count(self) -> int:
        """Return the number of documents in the store"""
        return len(self.ids)

    def reset(self):
        """Clear all data"""
        self.embeddings = []
        self.metadata = []
        self.ids = []
        self.documents = []
        
        # Delete files
        for f in [self.embeddings_file, self.metadata_file, self.ids_file, self.documents_file]:
            if f.exists():
                f.unlink()

