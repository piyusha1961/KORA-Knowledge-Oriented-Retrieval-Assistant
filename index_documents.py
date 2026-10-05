import os
import pickle
import faiss

from src.document_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import load_embedding_model, create_embeddings
from src.vector_store import create_vector_store


# --------------------------------
# Configuration
# --------------------------------

PDF_PATH = "data/sample_pdfs/DS_Exp_6_piyusha.pdf"

VECTOR_DB_DIR = "vector_db"

INDEX_PATH = os.path.join(
    VECTOR_DB_DIR,
    "faiss.index"
)

CHUNKS_PATH = os.path.join(
    VECTOR_DB_DIR,
    "chunks.pkl"
)


# --------------------------------
# Create vector database directory
# --------------------------------

os.makedirs(VECTOR_DB_DIR, exist_ok=True)


# --------------------------------
# 1. Load PDF
# --------------------------------

print("\nLoading PDF...")

pages = extract_text_from_pdf(PDF_PATH)

print(f"Pages extracted: {len(pages)}")


# --------------------------------
# 2. Create chunks
# --------------------------------

print("\nCreating chunks...")

chunks = create_chunks(pages)

print(f"Chunks created: {len(chunks)}")


# --------------------------------
# 3. Load embedding model
# --------------------------------

print("\nLoading embedding model...")

model = load_embedding_model()

print("Embedding model loaded.")


# --------------------------------
# 4. Create embeddings
# --------------------------------

print("\nCreating embeddings...")

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = create_embeddings(
    model,
    texts
)

print(f"Embeddings created: {len(embeddings)}")


# --------------------------------
# 5. Create FAISS index
# --------------------------------

print("\nCreating FAISS index...")

index = create_vector_store(
    embeddings
)

print(f"FAISS index contains {index.ntotal} vectors")


# --------------------------------
# 6. Save FAISS index
# --------------------------------

faiss.write_index(
    index,
    INDEX_PATH
)

print(f"FAISS index saved to: {INDEX_PATH}")


# --------------------------------
# 7. Save chunks + metadata
# --------------------------------

with open(CHUNKS_PATH, "wb") as file:

    pickle.dump(
        chunks,
        file
    )

print(f"Chunks saved to: {CHUNKS_PATH}")


# --------------------------------
# Done
# --------------------------------

print("\n==============================")
print("INDEXING COMPLETE")
print("==============================")

print(f"Documents: {PDF_PATH}")
print(f"Pages: {len(pages)}")
print(f"Chunks: {len(chunks)}")
print(f"Vectors: {index.ntotal}")