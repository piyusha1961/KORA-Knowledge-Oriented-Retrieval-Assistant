import os

from src.document_loader import extract_text_from_pdf
from src.document_registry import add_document


# ==================================================
# EXISTING DOCUMENTS
# ==================================================

DOCUMENTS = [
    "data/sample_pdfs/DS_Exp_6_piyusha.pdf",
]


# ==================================================
# ADD EXISTING UPLOADED PDF
# ==================================================

uploaded_dir = "data/uploaded_pdfs"

if os.path.exists(uploaded_dir):

    for filename in os.listdir(uploaded_dir):

        if filename.lower().endswith(".pdf"):

            DOCUMENTS.append(
                os.path.join(
                    uploaded_dir,
                    filename
                )
            )


# ==================================================
# REGISTER DOCUMENTS
# ==================================================

for pdf_path in DOCUMENTS:

    if not os.path.exists(pdf_path):

        print(
            f"⚠️ File not found: {pdf_path}"
        )

        continue


    print(
        f"\nRegistering: {pdf_path}"
    )


    # Extract pages only.
    # We are NOT creating embeddings here.

    pages = extract_text_from_pdf(
        pdf_path
    )


    document = add_document(
        pdf_path,
        pages=len(pages),
        chunks=0
    )


    print(
        f"Document ID: "
        f"{document['document_id']}"
    )

    print(
        f"Pages: {len(pages)}"
    )

    print(
        "✅ Registered"
    )


print(
    "\n=============================="
)

print(
    "DOCUMENT MIGRATION COMPLETE"
)

print(
    "=============================="
)