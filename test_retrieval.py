import pickle
import faiss

from src.embeddings import load_embedding_model, create_embeddings
from src.vector_store import search_vector_store


INDEX_PATH = "vector_db/faiss.index"
CHUNKS_PATH = "vector_db/chunks.pkl"


# Load FAISS index
index = faiss.read_index(INDEX_PATH)

# Load chunks
with open(CHUNKS_PATH, "rb") as file:
    chunks = pickle.load(file)

# Load embedding model
model = load_embedding_model()


questions = [
    "What is the problem statement?",
    "What tasks are performed in this experiment?",
    "What are the objectives of the experiment?"
]


for question in questions:

    print("\n")
    print("=" * 70)
    print(f"QUESTION: {question}")
    print("=" * 70)

    # Create query embedding
    query_embedding = create_embeddings(
        model,
        [question]
    )

    # Ask FAISS for ALL chunks
    scores, indices = search_vector_store(
        index,
        query_embedding,
        top_k=len(chunks)
    )

    for rank, (score, index_number) in enumerate(
        zip(scores, indices),
        start=1
    ):

        chunk = chunks[index_number]

        print("\n" + "-" * 60)
        print(f"RANK: {rank}")
        print(f"Chunk index: {index_number}")
        print(f"Similarity: {score:.4f}")
        print(f"Page: {chunk['page']}")
        print("\nText:")
        print(chunk["text"])