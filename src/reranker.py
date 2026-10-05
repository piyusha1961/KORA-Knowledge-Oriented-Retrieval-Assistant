from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def load_reranker():
    """
    Load the local CrossEncoder reranking model.
    """

    return CrossEncoder(MODEL_NAME)


def rerank_documents(
    question,
    documents,
    reranker,
    top_k=3
):
    """
    Rerank retrieved documents according to
    their relevance to the user's question.
    """

    if not documents:
        return []

    pairs = [
        (question, document["text"])
        for document in documents
    ]

    scores = reranker.predict(pairs)

    reranked_documents = []

    for document, score in zip(documents, scores):

        updated_document = document.copy()

        updated_document["rerank_score"] = float(score)

        reranked_documents.append(updated_document)

    reranked_documents.sort(
        key=lambda document: document["rerank_score"],
        reverse=True
    )

    return reranked_documents[:top_k]