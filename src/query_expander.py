QUERY_ALIASES = {
    "objectives": [
        "problem statement",
        "tasks performed",
        "goals of the experiment"
    ],
    "tasks": [
        "problem statement",
        "objectives",
        "requirements"
    ],
    "purpose": [
        "problem statement",
        "objectives",
        "goals"
    ]
}


def expand_query(question):
    """
    Expand a user question with related terminology
    to improve semantic retrieval.
    """

    question_lower = question.lower()

    expanded_queries = [question]

    for keyword, alternatives in QUERY_ALIASES.items():

        if keyword in question_lower:

            expanded_queries.extend(alternatives)

    return expanded_queries