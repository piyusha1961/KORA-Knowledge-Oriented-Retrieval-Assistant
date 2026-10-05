import os
import pickle
import faiss

from src.document_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import create_embeddings
from src.document_registry import (
    add_document,
    generate_document_id,
    document_exists,
    get_document,
    remove_document
)


VECTOR_DB_DIR = "vector_db"

INDEX_PATH = os.path.join(
    VECTOR_DB_DIR,
    "faiss.index"
)

CHUNKS_PATH = os.path.join(
    VECTOR_DB_DIR,
    "chunks.pkl"
)


# ============================================================
# ADD PDF TO VECTOR STORE
# ============================================================

def add_pdf_to_vector_store(
    pdf_path,
    embedding_model
):
    """
    Process a PDF, create embeddings,
    add them to FAISS, and register the document.
    """

    # --------------------------------------------------------
    # GENERATE DOCUMENT ID
    # --------------------------------------------------------

    document_id = generate_document_id(
        pdf_path
    )

    if document_exists(document_id):

        raise ValueError(
            "This document has already been indexed."
        )


    # --------------------------------------------------------
    # EXTRACT PDF TEXT
    # --------------------------------------------------------

    pages = extract_text_from_pdf(
        pdf_path
    )

    if not pages:

        raise ValueError(
            "No text could be extracted from the PDF."
        )


    # --------------------------------------------------------
    # CREATE CHUNKS
    # --------------------------------------------------------

    chunks = create_chunks(
        pages
    )

    if not chunks:

        raise ValueError(
            "No chunks were created from the PDF."
        )


    # --------------------------------------------------------
    # ADD DOCUMENT METADATA TO EACH CHUNK
    # --------------------------------------------------------

    filename = os.path.basename(
        pdf_path
    )

    for chunk in chunks:

        chunk["document_id"] = document_id

        chunk["filename"] = filename


    # --------------------------------------------------------
    # CREATE EMBEDDINGS
    # --------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = create_embeddings(
        embedding_model,
        texts
    )


    # --------------------------------------------------------
    # LOAD OR CREATE FAISS INDEX
    # --------------------------------------------------------

    if os.path.exists(INDEX_PATH):

        index = faiss.read_index(
            INDEX_PATH
        )

    else:

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )


    # --------------------------------------------------------
    # ADD VECTORS
    # --------------------------------------------------------

    index.add(
        embeddings.astype("float32")
    )


    # --------------------------------------------------------
    # LOAD EXISTING CHUNKS
    # --------------------------------------------------------

    if os.path.exists(CHUNKS_PATH):

        with open(
            CHUNKS_PATH,
            "rb"
        ) as file:

            existing_chunks = pickle.load(
                file
            )

    else:

        existing_chunks = []


    # --------------------------------------------------------
    # ADD NEW CHUNKS
    # --------------------------------------------------------

    existing_chunks.extend(
        chunks
    )


    # --------------------------------------------------------
    # SAVE FAISS INDEX
    # --------------------------------------------------------

    os.makedirs(
        VECTOR_DB_DIR,
        exist_ok=True
    )

    faiss.write_index(
        index,
        INDEX_PATH
    )


    # --------------------------------------------------------
    # SAVE CHUNKS
    # --------------------------------------------------------

    with open(
        CHUNKS_PATH,
        "wb"
    ) as file:

        pickle.dump(
            existing_chunks,
            file
        )


    # --------------------------------------------------------
    # REGISTER DOCUMENT
    # --------------------------------------------------------

    document = add_document(
        pdf_path,
        pages=len(pages),
        chunks=len(chunks)
    )


    # --------------------------------------------------------
    # RETURN STATISTICS
    # --------------------------------------------------------

    return {
        "document_id": document_id,
        "filename": filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "total_chunks": len(existing_chunks),
        "total_vectors": index.ntotal
    }


# ============================================================
# DELETE DOCUMENT FROM VECTOR STORE
# ============================================================

def delete_document_from_vector_store(
    document_id,
    embedding_model
):
    """
    Delete a document and its chunks.

    Because the current FAISS index is IndexFlatIP
    without persistent vector IDs, the index is rebuilt
    from the remaining chunks.
    """

    # --------------------------------------------------------
    # FIND DOCUMENT IN REGISTRY
    # --------------------------------------------------------

    document = get_document(
        document_id
    )

    if document is None:

        raise ValueError(
            "Document not found in registry."
        )


    filename = document["filename"]


    # --------------------------------------------------------
    # LOAD EXISTING CHUNKS
    # --------------------------------------------------------

    if not os.path.exists(CHUNKS_PATH):

        raise ValueError(
            "chunks.pkl not found."
        )


    with open(
        CHUNKS_PATH,
        "rb"
    ) as file:

        existing_chunks = pickle.load(
            file
        )


    # --------------------------------------------------------
    # SEPARATE DOCUMENT CHUNKS
    # --------------------------------------------------------

    remaining_chunks = []

    deleted_chunks = []


    for chunk in existing_chunks:

        chunk_document_id = chunk.get(
            "document_id"
        )

        chunk_filename = chunk.get(
            "filename"
        )


        # ----------------------------------------------------
        # NEWER CHUNKS HAVE document_id
        # ----------------------------------------------------

        if chunk_document_id == document_id:

            deleted_chunks.append(
                chunk
            )

            continue


        # ----------------------------------------------------
        # OLD/MIGRATED CHUNKS MAY NOT HAVE document_id
        #
        # Use filename as fallback.
        # ----------------------------------------------------

        if (
            chunk_document_id is None
            and chunk_filename == filename
        ):

            deleted_chunks.append(
                chunk
            )

            continue


        # ----------------------------------------------------
        # KEEP EVERYTHING ELSE
        # ----------------------------------------------------

        remaining_chunks.append(
            chunk
        )


    # --------------------------------------------------------
    # CHECK WHETHER CHUNKS WERE FOUND
    # --------------------------------------------------------

    deleted_count = len(
        deleted_chunks
    )


    if deleted_count == 0:

        raise ValueError(
            "No chunks belonging to this document "
            "were found in the vector database."
        )


    # --------------------------------------------------------
    # REBUILD FAISS INDEX
    # --------------------------------------------------------

    if remaining_chunks:

        remaining_texts = [
            chunk["text"]
            for chunk in remaining_chunks
        ]

        remaining_embeddings = create_embeddings(
            embedding_model,
            remaining_texts
        )

        dimension = (
            remaining_embeddings.shape[1]
        )

        new_index = faiss.IndexFlatIP(
            dimension
        )

        new_index.add(
            remaining_embeddings.astype(
                "float32"
            )
        )

    else:

        # ----------------------------------------------------
        # If no documents remain, create an empty index
        # using the embedding dimension.
        # ----------------------------------------------------

        dimension = 384

        new_index = faiss.IndexFlatIP(
            dimension
        )


    # --------------------------------------------------------
    # SAVE NEW FAISS INDEX
    # --------------------------------------------------------

    faiss.write_index(
        new_index,
        INDEX_PATH
    )


    # --------------------------------------------------------
    # SAVE REMAINING CHUNKS
    # --------------------------------------------------------

    with open(
        CHUNKS_PATH,
        "wb"
    ) as file:

        pickle.dump(
            remaining_chunks,
            file
        )


    # --------------------------------------------------------
    # REMOVE DOCUMENT FROM REGISTRY
    # --------------------------------------------------------

    removed = remove_document(
        document_id
    )


    if not removed:

        raise ValueError(
            "Document chunks were removed, "
            "but registry removal failed."
        )


    # --------------------------------------------------------
    # RETURN STATISTICS
    # --------------------------------------------------------

    return {
        "document_id": document_id,
        "filename": filename,
        "deleted_chunks": deleted_count,
        "remaining_chunks": len(
            remaining_chunks
        ),
        "remaining_vectors": new_index.ntotal
    }