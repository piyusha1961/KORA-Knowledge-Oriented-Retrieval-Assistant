from src.embeddings import create_embeddings
from src.vector_store import search_vector_store
from src.query_expander import expand_query
from src.reranker import rerank_documents
from src.query_intent import detect_query_intent


# Which document sections are relevant to each intent
INTENT_SECTION_MAP = {
    "objective": [
        "Problem Statement"
    ],

    "procedure": [
        "Algorithm Steps",
        "Program"
    ],

    "definition": [
        "Problem Statement",
        "Algorithm Steps",
        "Program"
    ],

    "conclusion": [
        "Conclusion"
    ],

    "count": [
        "Algorithm Steps",
        "Program"
    ],

    "general": []
}


def retrieve_documents(
    question,
    model,
    index,
    chunks,
    reranker,
    candidate_k=8,
    final_k=3
):

    # --------------------------------------------------
    # 1. Detect query intent
    # --------------------------------------------------

    intent = detect_query_intent(question)

    preferred_sections = INTENT_SECTION_MAP.get(
        intent,
        []
    )

    print(f"\nDetected intent: {intent}")

    if preferred_sections:
        print(
            f"Preferred sections: "
            f"{', '.join(preferred_sections)}"
        )

    # --------------------------------------------------
    # 2. Expand the query
    # --------------------------------------------------

    queries = expand_query(question)

    # --------------------------------------------------
    # 3. Retrieve FAISS candidates
    # --------------------------------------------------

    candidate_scores = {}

    for query in queries:

        query_embedding = create_embeddings(
            model,
            [query]
        )

        scores, indices = search_vector_store(
            index,
            query_embedding,
            top_k=candidate_k
        )

        for score, index_number in zip(
            scores,
            indices
        ):

            # Ignore invalid FAISS results
            if (
                index_number < 0
                or index_number >= len(chunks)
            ):
                continue

            score = float(score)

            # Keep the best FAISS score obtained
            # for each chunk
            if index_number not in candidate_scores:

                candidate_scores[index_number] = score

            else:

                candidate_scores[index_number] = max(
                    candidate_scores[index_number],
                    score
                )

    # --------------------------------------------------
    # 4. Build candidate documents
    # --------------------------------------------------

    candidate_documents = []

    for index_number, score in candidate_scores.items():

        chunk = chunks[index_number]

        # Start with the original FAISS similarity
        adjusted_score = score

        section = chunk.get(
            "section",
            None
        )

        # --------------------------------------------------
        # 5. Intent-aware section boost
        # --------------------------------------------------

        if section in preferred_sections:

            adjusted_score += 0.20

        candidate_documents.append({

            "text": chunk["text"],

            "page": chunk["page"],

            "pages": chunk.get(
                "pages",
                [chunk["page"]]
            ),

            "source": chunk["source"],

            "section": section,

            "score": score,

            "adjusted_score": adjusted_score
        })

    # --------------------------------------------------
    # 6. Sort using intent-aware score
    # --------------------------------------------------

    candidate_documents.sort(
        key=lambda document:
            document["adjusted_score"],
        reverse=True
    )

    # --------------------------------------------------
    # 7. Rerank candidates using the cross-encoder
    # --------------------------------------------------

    reranked_documents = rerank_documents(
        question,
        candidate_documents,
        reranker,
        top_k=len(candidate_documents)
    )


    # --------------------------------------------------
    # 8. Apply intent-aware ranking AFTER reranking
    # --------------------------------------------------

    for document in reranked_documents:

        rerank_score = document["rerank_score"]

        intent_boost = 0.0

        if document.get("section") in preferred_sections:
            intent_boost = 2.0

        document["final_score"] = (
            rerank_score + intent_boost
        )


    # --------------------------------------------------
    # 9. Sort using final score
    # --------------------------------------------------

    reranked_documents.sort(
        key=lambda document:
            document["final_score"],
        reverse=True
    )


    # --------------------------------------------------
    # 10. Return only the final top-k
    # --------------------------------------------------

    return reranked_documents[:final_k]