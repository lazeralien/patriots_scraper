import json
from pathlib import Path

# Paths
results_file = "results_forum.json"
queries_file = "data/forum_queries.txt"
posts_dir = Path("posts")

# Load queries
with open(queries_file, "r", encoding="utf-8") as f:
    queries = [line.strip() for line in f]

# Load results
with open(results_file, "r", encoding="utf-8") as f:
    data = json.load(f)
results = data["results"]

# Build a docid -> url mapping
docid_to_url = {}
for f in posts_dir.glob("post_*.json"):
    try:
        post_data = json.load(open(f, encoding="utf-8"))
        docid_to_url[post_data["id"]] = post_data.get("url", "")
    except:
        continue

# Print top 10 results per query
for i, query in enumerate(queries, start=1):
    qid = str(i)
    print(f"\n=== Query {qid}: {query} ===")

    if qid not in results or not results[qid]:
        print("No results found.")
        continue

    top_hits = results[qid][:10]  # top 10
    for rank, (docid, score) in enumerate(top_hits, start=1):
        url = docid_to_url.get(docid, "URL not found")
        print(f"[{rank}] {url} | Score: {score:.4f}")
