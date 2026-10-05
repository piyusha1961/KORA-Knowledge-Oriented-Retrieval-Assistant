import os
import json
import hashlib


REGISTRY_PATH = "data/document_registry.json"


# ==================================================
# INITIALIZE REGISTRY
# ==================================================

def initialize_registry():

    os.makedirs(
        "data",
        exist_ok=True
    )

    if not os.path.exists(REGISTRY_PATH):

        with open(
            REGISTRY_PATH,
            "w"
        ) as file:

            json.dump(
                {
                    "documents": []
                },
                file,
                indent=4
            )


# ==================================================
# LOAD REGISTRY
# ==================================================

def load_registry():

    initialize_registry()

    with open(
        REGISTRY_PATH,
        "r"
    ) as file:

        return json.load(file)


# ==================================================
# SAVE REGISTRY
# ==================================================

def save_registry(registry):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        REGISTRY_PATH,
        "w"
    ) as file:

        json.dump(
            registry,
            file,
            indent=4
        )


# ==================================================
# GENERATE DOCUMENT ID
# ==================================================

def generate_document_id(file_path):

    """
    Generate a stable document ID using
    the file contents.
    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()[:16]


# ==================================================
# CHECK WHETHER DOCUMENT EXISTS
# ==================================================

def document_exists(
    document_id
):

    registry = load_registry()

    for document in registry["documents"]:

        if document["document_id"] == document_id:

            return True

    return False


# ==================================================
# ADD DOCUMENT
# ==================================================

def add_document(
    file_path,
    pages,
    chunks
):

    registry = load_registry()

    document_id = generate_document_id(
        file_path
    )

    # ----------------------------------------------
    # Prevent duplicate documents
    # ----------------------------------------------

    for document in registry["documents"]:

        if document["document_id"] == document_id:

            return document


    # ----------------------------------------------
    # Create document record
    # ----------------------------------------------

    document = {

        "document_id": document_id,

        "filename": os.path.basename(
            file_path
        ),

        "source": file_path,

        "pages": pages,

        "chunks": chunks

    }


    registry["documents"].append(
        document
    )


    save_registry(
        registry
    )


    return document


# ==================================================
# GET ALL DOCUMENTS
# ==================================================

def get_documents():

    registry = load_registry()

    return registry["documents"]


# ==================================================
# GET DOCUMENT BY ID
# ==================================================

def get_document(
    document_id
):

    registry = load_registry()

    for document in registry["documents"]:

        if document["document_id"] == document_id:

            return document

    return None


# ==================================================
# REMOVE DOCUMENT
# ==================================================

def remove_document(
    document_id
):

    registry = load_registry()

    original_count = len(
        registry["documents"]
    )

    registry["documents"] = [
        document
        for document in registry["documents"]
        if document["document_id"] != document_id
    ]

    save_registry(
        registry
    )

    return (
        len(registry["documents"])
        < original_count
    )