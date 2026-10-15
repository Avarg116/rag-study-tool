import sys

import psycopg
from anthropic import Anthropic
from psycopg.rows import dict_row

from app.config import settings
from app.services.embeddings import embed_text
from app.services.retrieval import vector_search

client = Anthropic(api_key=settings.anthropic_api_key)

# 1. define tools
TOOLS = [
    {
        "name": "search",
        "description": "Search the uploaded study materials. Returns the 5 closest chunks.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "submit_evidence",
        "description": "Finish by submitting up to 5 chunk ids (like C1) that answer the question, most relevant first.",
        "input_schema": {
            "type": "object",
            "properties": {"chunk_ids": {"type": "array", "items": {"type": "string"}}},
            "required": ["chunk_ids"],
        },
    },
]

SYSTEM_PROMPT = """You find passages in the user's study materials that answer their question.
Use the search tool. If the results don't answer the question, search again with different words.
When you have what you need, call submit_evidence with up to 5 chunk ids from the results,
most relevant first. Do not answer the question yourself."""

# 2. run when the model calls the tool
def run_search(conn, query, seen):
    rows = vector_search(conn, embed_text(query), settings.top_k)
    seen_ids = [row["id"] for row in seen]
    results = []
    for row in rows:
        if row["id"] not in seen_ids:
            seen.append(row)
            seen_ids.append(row["id"])
        label = f"C{seen_ids.index(row['id']) + 1}"
        results.append(f"[{label}] {row['filename']}, page {row['page_number']}:\n{row['content']}")
    return "\n\n".join(results) or "No chunks found."

# 3. the agent loop
def run_agent(conn, question, max_steps=5):
    messages = [{"role": "user", "content": question}]
    seen = []

    for step in range(max_steps):
        response = client.messages.create(
            model=settings.agent_model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            if block.name == "submit_evidence":
                print(f"step {step + 1}: submit_evidence({block.input['chunk_ids']})")
                labels = {f"C{i + 1}": row for i, row in enumerate(seen)}
                chosen = []
                for c in block.input["chunk_ids"]:
                    if c in labels and labels[c] not in chosen:
                        chosen.append(labels[c])
                return chosen[:settings.top_k] or seen[:settings.top_k]

            print(f"step {step + 1}: search({block.input['query']!r})")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": run_search(conn, block.input["query"], seen),
            })
        messages.append({"role": "user", "content": tool_results})

    return seen[:settings.top_k]

# 4. test: python -m app.services.search_agent "your question"
if __name__ == "__main__":
    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        for row in run_agent(conn, sys.argv[1]):
            print(f"  {row['filename']}, page {row['page_number']}")
