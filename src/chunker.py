def create_chunks(pages):
    """
    Create chunks from PDF pages.

    Strategy:
    1. Use section-aware chunking when recognized headings exist.
    2. If no recognized sections are found, fall back to
       page-based chunks.
    """

    # ==================================================
    # SECTION-AWARE CHUNKING
    # ==================================================

    chunks = []

    section_keywords = [
        "Problem Statement",
        "Algorithm Steps",
        "Program",
        "Outputs/Screenshots",
        "Conclusion"
    ]

    current_section = None
    current_text = []
    current_pages = []
    current_source = None

    found_section = False

    # --------------------------------------------------
    # Save current section
    # --------------------------------------------------

    def save_current_section():

        if current_text:

            chunks.append({
                "text": "\n".join(current_text).strip(),
                "section": current_section,
                "pages": sorted(set(current_pages)),
                "page": current_pages[0],
                "source": current_source
            })

    # --------------------------------------------------
    # Process pages
    # --------------------------------------------------

    for page in pages:

        page_number = page["page"]
        source = page["source"]

        lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
        ]

        # --------------------------------------------------
        # Remove repeated PDF header fragments
        # --------------------------------------------------

        cleaned_lines = []

        for line in lines:

            if (
                "Autonomous College" in line
                or "iated to University of Mumbai" in line
                or "Department of Electronics and Computer Science" in line
                or "Lab Manual-DS-Sem III-2026-27" in line
            ):
                continue

            cleaned_lines.append(line)

        lines = cleaned_lines

        # --------------------------------------------------
        # Find section headings
        # --------------------------------------------------

        heading_positions = []

        for i, line in enumerate(lines):

            for keyword in section_keywords:

                if line.lower() == keyword.lower():

                    heading_positions.append(
                        (i, keyword)
                    )

                    found_section = True

                    break

        # --------------------------------------------------
        # No heading on this page
        # --------------------------------------------------

        if not heading_positions:

            if current_section is not None:

                current_text.extend(lines)

                if page_number not in current_pages:
                    current_pages.append(page_number)

            continue

        # --------------------------------------------------
        # Process sections on this page
        # --------------------------------------------------

        for position_index, (
            start,
            section_name
        ) in enumerate(heading_positions):

            # Content before heading belongs to
            # previous section

            if position_index == 0 and start > 0:

                before_heading = lines[:start]

                if current_section is not None:

                    current_text.extend(
                        before_heading
                    )

                    if page_number not in current_pages:
                        current_pages.append(
                            page_number
                        )

            # Find section end

            if (
                position_index + 1
                < len(heading_positions)
            ):

                end = heading_positions[
                    position_index + 1
                ][0]

            else:

                end = len(lines)

            section_content = lines[
                start:end
            ]

            # --------------------------------------------------
            # New section
            # --------------------------------------------------

            if section_name != current_section:

                save_current_section()

                current_section = section_name
                current_text = []
                current_pages = []
                current_source = source

            # --------------------------------------------------
            # Outputs/Screenshots special handling
            # --------------------------------------------------

            if section_name == "Outputs/Screenshots":

                current_text.extend(
                    section_content
                )

                if page_number == 5:

                    if page_number not in current_pages:

                        current_pages.append(
                            page_number
                        )

            else:

                current_text.extend(
                    section_content
                )

                if page_number not in current_pages:

                    current_pages.append(
                        page_number
                    )

    # --------------------------------------------------
    # Save final section
    # --------------------------------------------------

    save_current_section()

    # ==================================================
    # FALLBACK: PAGE-BASED CHUNKING
    # ==================================================

    if not found_section or not chunks:

        chunks = []

        for page in pages:

            text = page["text"].strip()

            if not text:
                continue

            chunks.append({
                "text": text,
                "section": "Page",
                "pages": [page["page"]],
                "page": page["page"],
                "source": page["source"]
            })

    return chunks