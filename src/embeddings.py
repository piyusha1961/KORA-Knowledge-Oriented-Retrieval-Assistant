from sentence_transformers import SentenceTransformer


# Lightweight model that runs locally
MODEL_NAME = "all-MiniLM-L6-v2"


def load_embedding_model():
    """
    Load the local embedding model.
    """
    return SentenceTransformer(MODEL_NAME)


def create_embeddings(model, texts):
    """
    Convert text chunks into numerical vectors.
    """
    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )