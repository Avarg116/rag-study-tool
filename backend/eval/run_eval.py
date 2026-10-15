import json
import psycopg
from psycopg.rows import dict_row

from app.config import settings
from app.services.embeddings import embed_text
from app.services.retrieval import vector_search

K = 5

with open("eval/questions.json") as f:
    data = json.load(f)
document = data["document"]
conn = psycopg.connect(settings.database_url, row_factory=dict_row)

def first_hit_rank(rows, expected_pages):
    for rank, row in enumerate(rows, start=1):
        if row["filename"] == document and row["page_number"] in expected_pages:
            return rank
    return None

def summary(label, ranks):
    n = len(ranks)
    hit1 = ranks.count(1) / n
    hitk = (n - ranks.count(None)) / n
    mrr = sum(1 / r for r in ranks if r is not None) / n
    print(f"{label}: Hit@1 {hit1:.1%}, Hit@{K} {hitk:.1%}, MRR {mrr:.3f} ({n} questions)")

results = []
for q in data["questions"]:
    rows = vector_search(conn, embed_text(q["question"]), K)
    rank = first_hit_rank(rows, q["expected_pages"])
    results.append((q, rank))
    result = "miss" if rank is None else f"rank {rank}"
    print(f"{q['id']:<4} {result:<7} {q['question']}")

print()
summary("ALL", [rank for _, rank in results])
for question_type in ["exact-term", "factual", "paraphrase"]:
    summary(question_type, [rank for q, rank in results if q["type"] == question_type])
