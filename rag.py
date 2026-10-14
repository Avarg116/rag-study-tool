import numpy as np
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = Anthropic()

# 1. load the notes and split them into chunks (1 paragraph = 1 chunk)
with open("notes.txt") as f:
    chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
print(f"{len(chunks)} chunks")

# 2. indexing: store each chunk with its vector
vector_db = [(chunk, model.encode(chunk)) for chunk in chunks]
print(f"vector size: {len(vector_db[0][1])}")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 3. retrieval: compare the question to every chunk and keep the best ones
def retrieve(question, top_n=3):
    question_vector = model.encode(question)
    scored = [(chunk, cosine_similarity(question_vector, vector)) for chunk, vector in vector_db]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]

# 4. generation: give the model the chunks and the question
def ask(question):
    results = retrieve(question)
    print(f"\nQuestion: {question}")
    for chunk, score in results:
        print(f"  {score:.2f}  {chunk[:70]}...")

    context = "\n\n".join(chunk for chunk, _ in results)
    prompt = f"""Answer the question using only the context below.
If the context doesn't contain the answer, say you don't know.

Context:
{context}

Question: {question}"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    print(f"Answer: {response.content[0].text}")


ask("Where does the Calvin cycle happen?")
ask("How does the cell make most of its ATP?")
ask("What is the capital of France?")
