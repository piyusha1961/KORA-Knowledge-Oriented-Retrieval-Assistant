from src.query_expander import expand_query


questions = [
    "What are the objectives of the experiment?",
    "What tasks are performed in this experiment?",
    "What is the problem statement?"
]


for question in questions:

    print("\nQuestion:")
    print(question)

    print("\nExpanded queries:")

    for query in expand_query(question):
        print("-", query)