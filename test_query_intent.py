from src.query_intent import detect_query_intent


questions = [
    "What are the objectives?",
    "How is a linked list created?",
    "What is a linked list?",
    "What is the conclusion?",
    "How many nodes are there?",
    "Tell me about the experiment"
]


for question in questions:
    intent = detect_query_intent(question)

    print(f"Question: {question}")
    print(f"Intent:   {intent}")
    print("-" * 50)