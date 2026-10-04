from backend.app.ai.embeddings import EmbeddingService


def test_embedding_service_generates_vectors():
    service = EmbeddingService(model_name='all-MiniLM-L6-v2')
    vectors = service.embed_documents(['Alpha launch plan', 'Beta release schedule'])
    assert len(vectors) == 2
    assert vectors[0].shape[0] > 0
