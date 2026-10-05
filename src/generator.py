import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"


def generate_answer(question, retrieved_documents):
    """
    Generate an answer using Qwen3 and the retrieved document chunks.
    """

    # --------------------------------
    # 1. Build context from retrieved chunks
    # --------------------------------

    context = "\n\n".join(
        [
            f"[Pages {', '.join(map(str, doc['pages']))}]\n{doc['text']}"
            for doc in retrieved_documents
        ]
    )


    # --------------------------------
    # 2. Create prompt
    # --------------------------------

    prompt = f"""
You are a helpful document-based question answering assistant.

Answer the user's question using ONLY the provided context.

Important rules:
1. Do not use outside knowledge.
2. Do not make up information.
3. If the answer cannot be found in the context, say:
   "I could not find the answer in the provided document."
4. Whenever you use information from the context, include the relevant
   page citation in the format [Page X].
5. Keep the answer concise and clear.

Context:
{context}

Question:
{question}

Answer:
"""


    # --------------------------------
    # 3. Send request to Ollama
    # --------------------------------

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
    )


    # --------------------------------
    # 4. Check response
    # --------------------------------

    response.raise_for_status()


    # --------------------------------
    # 5. Extract answer
    # --------------------------------

    result = response.json()

    return result["message"]["content"]