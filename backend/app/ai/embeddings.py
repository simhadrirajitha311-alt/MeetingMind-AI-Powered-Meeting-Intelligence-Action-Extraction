import hashlib
import json
from pathlib import Path

import faiss
import numpy as np

from backend.app.core.config import settings


class EmbeddingService:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self.vector_size = 128
        self.store_dir = Path(__file__).resolve().parents[2] / 'data' / 'vector_store'
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def _hash_vector(self, value: str) -> np.ndarray:
        normalized = value.lower().strip()
        digest = hashlib.sha256(normalized.encode('utf-8')).digest()
        vector = np.frombuffer(digest, dtype=np.uint8).astype(np.float32)
        if vector.size < self.vector_size:
            vector = np.pad(vector, (0, self.vector_size - vector.size), mode='constant')
        return vector[:self.vector_size] / 255.0

    def embed_text(self, text: str) -> np.ndarray:
        return self._hash_vector(text)

    def embed_documents(self, texts):
        return np.vstack([self.embed_text(text) for text in texts]) if texts else np.zeros((0, self.vector_size), dtype='float32')

    def build_index(self, texts):
        vectors = self.embed_documents(texts)
        if vectors.size == 0:
            vectors = np.zeros((1, self.vector_size), dtype='float32')
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors.astype('float32'))
        return index, vectors

    def save_index(self, meeting_id: int, chunks):
        texts = [chunk['text'] for chunk in chunks]
        index, _ = self.build_index(texts)
        meeting_dir = self.store_dir / str(meeting_id)
        meeting_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(meeting_dir / 'index.faiss'))
        with open(meeting_dir / 'metadata.json', 'w', encoding='utf-8') as handle:
            json.dump(chunks, handle, ensure_ascii=False)
        return {'index_path': str(meeting_dir / 'index.faiss'), 'metadata_path': str(meeting_dir / 'metadata.json')}

    def load_index(self, meeting_id: int):
        meeting_dir = self.store_dir / str(meeting_id)
        index_path = meeting_dir / 'index.faiss'
        metadata_path = meeting_dir / 'metadata.json'
        if not index_path.exists() or not metadata_path.exists():
            return None, []

        index = faiss.read_index(str(index_path))
        with open(metadata_path, 'r', encoding='utf-8') as handle:
            metadata = json.load(handle)
        return index, metadata

    def similarity_search(self, meeting_id: int, query: str, top_k: int = 5):
        index, metadata = self.load_index(meeting_id)
        if index is None:
            return []
        query_vector = self.embed_text(query)
        formatted = np.asarray([query_vector], dtype='float32')
        scores, indices = index.search(formatted, min(top_k, len(metadata)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(metadata):
                continue
            item = metadata[int(idx)]
            results.append({
                'text': item.get('text', ''),
                'speaker': item.get('speaker', 'Speaker 1'),
                'start_time': float(item.get('start_time', 0.0)),
                'score': float(score),
            })
        return results
