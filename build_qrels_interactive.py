import os
import random
import textwrap
from pathlib import Path
import json

OUT = Path("posts")
QUERIES_FILE = "data/forum_queries.txt"
QRELS_FILE = "qrels.txt"
CHECKPOINT_FILE = "qrels_progress.json"

WRAP_WIDTH = 100  # number of characters per line
NUM_DOCS_PER_QUERY = 10  # how many candidates to show per query
SNIPPET_LENGTH = 800  # how much text to show by default


def search_docs(query, posts):
    """Simple keyword search over .txt files."""
    qwords = query.lower().split()
    scored = []
    for pid, text in posts.items():
        score = sum(text.lower().count(w) for w in qwords)
        if score > 0:
            scored.append((score, pid))
    return [pid for _, pid in sorted(scored, reverse=True)[:NUM_DOCS_PER_QUERY]]


def display_text(text, width=WRAP_WIDTH, pause_every=30):
    """Pretty print long text with line wrapping and paging."""
    wrapper = textwrap.TextWrapper(width=width)
    lines = wrapper.wrap(text)
    for i, line in enumerate(lines, start=1):
        print(line)
        if i % pause_every == 0:
            cont = input("Press Enter to continue or 'q' to stop viewing: ")
            if cont.lower().startswith("q"):
                break


# Load posts
posts = {}
for f in OUT.glob("post_*.txt"):
    posts[f.stem.replace("post_", "")] = f.read_text(encoding="utf-8")

# Load queries
queries = [q.strip() for q in open(QUERIES_FILE, encoding="utf-8") if q.strip()]

if not queries:
    raise SystemExit("forum_queries.txt is empty.")

print(f"Loaded {len(queries)} queries and {len(posts)} posts.")

# Load progress (if any)
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        progress = json.load(f)
else:
    progress = {}

with open(QRELS_FILE, "a", encoding="utf-8") as fout:
    for qid, query in enumerate(queries, start=1):
        if str(qid) in progress:
            print(f"\nSkipping Query {qid}: {query} (already labeled)")
            continue

        print(f"\n=== Query {qid}: {query} ===")
        hits = search_docs(query, posts)
        random.shuffle(hits)
        hits = hits[:NUM_DOCS_PER_QUERY]

        judgments = {}
        for pid in hits:
            text = posts[pid].replace("\n", " ")
            snippet = text[:SNIPPET_LENGTH]
            print(f"\n📄 [Post {pid}] Snippet:\n{'-' * 60}")
            display_text(snippet)
            print("-" * 60)
            print("Options: [y] relevant  [n] not relevant  [v] view full post  [q] quit")

            while True:
                ans = input("Your choice: ").strip().lower()
                if ans == "v":
                    print(f"\n=== Full Post {pid} ===")
                    display_text(text)
                    continue
                elif ans == "y":
                    rel = 1
                    break
                elif ans == "n":
                    rel = 0
                    break
                elif ans == "q":
                    # Save progress before quitting
                    progress[str(qid)] = True
                    with open(CHECKPOINT_FILE, "w") as f:
                        json.dump(progress, f, indent=2)
                    print("Progress saved. Exiting.")
                    exit()
                else:
                    print("Invalid input. Please enter y/n/v/q.")
            fout.write(f"{qid} 0 {pid} {rel}\n")
            fout.flush()

        progress[str(qid)] = True
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(progress, f, indent=2)

print("\n✅ Finished labeling all queries.")
