from src.document_registry import get_documents


documents = get_documents()


print("\n==============================")
print("REGISTERED DOCUMENTS")
print("==============================\n")


for document in documents:

    print(
        f"ID: {document['document_id']}"
    )

    print(
        f"File: {document['filename']}"
    )

    print(
        f"Pages: {document['pages']}"
    )

    print(
        f"Chunks: {document['chunks']}"
    )

    print(
        "------------------------------"
    )