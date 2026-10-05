import os
import pickle

from src.document_registry import (
    load_registry,
    save_registry
)


CHUNKS_PATH = "vector_db/chunks.pkl"


# ============================================================
# LOAD EXISTING CHUNKS
# ============================================================

if not os.path.exists(CHUNKS_PATH):

    print("❌ chunks.pkl not found.")

    exit()


with open(
    CHUNKS_PATH,
    "rb"
) as file:

    chunks = pickle.load(file)


print(
    f"Loaded {len(chunks)} total chunks."
)


# ============================================================
# LOAD DOCUMENT REGISTRY
# ============================================================

registry = load_registry()

documents = registry["documents"]


# ============================================================
# COUNT CHUNKS BY FILENAME
# ============================================================

chunk_counts = {}


for chunk in chunks:

    filename = chunk.get(
        "filename"
    )

    if filename:

        chunk_counts[filename] = (
            chunk_counts.get(filename, 0) + 1
        )

    else:

        source = chunk.get(
            "source",
            ""
        )

        filename = os.path.basename(
            source
        )

        if filename:

            chunk_counts[filename] = (
                chunk_counts.get(filename, 0) + 1
            )


# ============================================================
# UPDATE REGISTRY
# ============================================================

print("\nUpdating document registry...\n")


for document in documents:

    filename = document["filename"]

    count = chunk_counts.get(
        filename,
        0
    )

    document["chunks"] = count

    print(
        f"📄 {filename}"
    )

    print(
        f"   Pages: {document['pages']}"
    )

    print(
        f"   Chunks: {count}"
    )


# ============================================================
# SAVE REGISTRY
# ============================================================

save_registry(
    registry
)


print("\n==============================")
print("REGISTRY UPDATE COMPLETE")
print("==============================")

print(
    f"Total FAISS chunks: {len(chunks)}"
)
