import faiss
import numpy as np


def create_vector_store(embeddings):
    """
    Create a FAISS index from document embeddings.
    """

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(np.asarray(embeddings, dtype="float32"))

    return index


def search_vector_store(index, query_embedding, top_k=3):
    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    ).reshape(1, -1)

    # Never ask FAISS for more results than exist
    top_k = min(top_k, index.ntotal)

    scores, indices = index.search(query_embedding, top_k)

    return scores[0], indices[0]