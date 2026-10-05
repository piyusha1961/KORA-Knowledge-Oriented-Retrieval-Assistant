def detect_query_intent(question):
    """
    Detect the type of information the user is asking for.

    Returns one of:
    - objective
    - procedure
    - definition
    - conclusion
    - count
    - general
    """

    question_lower = question.lower()

    # Objective / purpose questions
    objective_keywords = [
        "objective",
        "objectives",
        "purpose",
        "goal",
        "goals",
        "aim",
        "aims",
        "what is the experiment about"
    ]

    # Procedure / implementation questions
    procedure_keywords = [
        "how",
        "steps",
        "procedure",
        "process",
        "implement",
        "implementation",
        "create",
        "created",
        "construct",
        "constructed"
    ]

    # Definition questions
    definition_keywords = [
        "what is",
        "what are",
        "define",
        "definition",
        "meaning"
    ]

    # Conclusion / result questions
    conclusion_keywords = [
        "conclusion",
        "result",
        "results",
        "outcome",
        "what did we achieve"
    ]

    # Counting / numerical questions
    count_keywords = [
        "how many",
        "number of",
        "count",
        "counted",
        "total"
    ]

    if any(keyword in question_lower for keyword in objective_keywords):
        return "objective"

    if any(keyword in question_lower for keyword in conclusion_keywords):
        return "conclusion"

    if any(keyword in question_lower for keyword in count_keywords):
        return "count"

    if any(keyword in question_lower for keyword in procedure_keywords):
        return "procedure"

    if any(keyword in question_lower for keyword in definition_keywords):
        return "definition"

    return "general"