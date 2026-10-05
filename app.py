import pickle
import faiss

from src.embeddings import load_embedding_model
from src.retriever import retrieve_documents
from src.generator import generate_answer
from src.reranker import load_reranker


INDEX_PATH = "vector_db/faiss.index"
CHUNKS_PATH = "vector_db/chunks.pkl"


# --------------------------------------------------
# Load FAISS index
# --------------------------------------------------

print("\nLoading vector database...")

index = faiss.read_index(INDEX_PATH)

print(
    f"FAISS index loaded: "
    f"{index.ntotal} vectors"
)


# --------------------------------------------------
# Load chunks
# --------------------------------------------------

with open(CHUNKS_PATH, "rb") as file:
    chunks = pickle.load(file)

print(
    f"Chunks loaded: "
    f"{len(chunks)}"
)


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

print("\nLoading embedding model...")

model = load_embedding_model()

print("Embedding model loaded.")


# --------------------------------------------------
# Load reranker
# --------------------------------------------------

print("\nLoading reranker...")

reranker = load_reranker()

print("Reranker loaded.")


# --------------------------------------------------
# Ask question
# --------------------------------------------------

question = input(
    "\nAsk a question about the document: "
)


# --------------------------------------------------
# Retrieve documents
# --------------------------------------------------

results = retrieve_documents(
    question,
    model,
    index,
    chunks,
    reranker,
    candidate_k=8,
    final_k=6
)


# --------------------------------------------------
# Display retrieved documents
# --------------------------------------------------

print("\n--- RETRIEVED DOCUMENTS ---")


for rank, result in enumerate(results, start=1):

    print("\n" + "-" * 50)

    print(f"Rank: {rank}")

    print(
        f"Section: "
        f"{result.get('section', 'N/A')}"
    )

    print(
        f"FAISS similarity: "
        f"{result['score']:.4f}"
    )

    print(
        f"Intent-adjusted score: "
        f"{result['adjusted_score']:.4f}"
    )

    print(
        f"Reranker score: "
        f"{result['rerank_score']:.4f}"
    )

    print(
        f"Final score: "
        f"{result['final_score']:.4f}"
    )

    print(
        f"Pages: "
        f"{result['pages']}"
    )

    print(
        f"Source: "
        f"{result['source']}"
    )

    print("\nText:")

    print(
        result["text"][:500]
    )


# --------------------------------------------------
# Generate final answer
# --------------------------------------------------

answer = generate_answer(
    question,
    results
)


# --------------------------------------------------
# Display final answer
# --------------------------------------------------

print("\n" + "=" * 60)

print("FINAL ANSWER")

print("=" * 60)

print(answer)