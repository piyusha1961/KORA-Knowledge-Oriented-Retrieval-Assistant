import pickle


CHUNKS_PATH = "vector_db/chunks.pkl"


with open(CHUNKS_PATH, "rb") as file:
    chunks = pickle.load(file)


print(f"\nTotal chunks: {len(chunks)}")


for i, chunk in enumerate(chunks):

    print("\n" + "=" * 60)
    print(f"CHUNK {i}")
    print("=" * 60)

    print(f"Section: {chunk.get('section', 'N/A')}")
    print(f"Page: {chunk['page']}")
    print(f"Pages: {chunk.get('pages', [chunk['page']])}")
    print(f"Source: {chunk['source']}")

    print("\n" + "-" * 60)
    print(chunk["text"])