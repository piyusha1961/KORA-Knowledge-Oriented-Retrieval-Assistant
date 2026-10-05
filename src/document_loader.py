import fitz


def extract_text_from_pdf(pdf_path):
    """
    Extract text from every page of a PDF.

    Returns:
        list: A list of dictionaries containing page text and metadata.
    """

    document = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text("text").strip()

        if text:
            pages.append({
                "text": text,
                "page": page_number + 1,
                "source": pdf_path
            })

    document.close()

    return pages