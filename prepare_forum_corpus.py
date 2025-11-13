# --------------------------------------------------------------
# prepare_forum_corpus.py — converts scraped forum posts into Pyserini JSON docs
# --------------------------------------------------------------
import json
from pathlib import Path
from tqdm import tqdm

POSTS_DIR = Path("posts")
OUT_DIR = Path("processed_corpus/patriots_forum")
OUT_DIR.mkdir(parents=True, exist_ok=True)

n_total = 0
n_converted = 0
n_skipped = 0

for json_file in tqdm(sorted(POSTS_DIR.glob("post_*.json")), desc="Preparing corpus"):
    n_total += 1
    try:
        # Load post metadata
        data = json.load(open(json_file, encoding="utf-8"))
        pid = data.get("id") or json_file.stem.split("_")[1]
        txt_file = POSTS_DIR / f"post_{pid}.txt"

        if not txt_file.exists():
            n_skipped += 1
            continue

        text = txt_file.read_text(encoding="utf-8").strip()
        if not text:
            n_skipped += 1
            continue

        # Construct Pyserini-compatible document
        out_doc = {
            "id": pid,
            "contents": text
        }

        # Write JSON document
        out_path = OUT_DIR / f"{pid}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out_doc, f)

        n_converted += 1

    except Exception as e:
        print(f"⚠️ Failed {json_file.name}: {e}")
        n_skipped += 1

print("\n===== Summary =====")
print(f"Total posts: {n_total}")
print(f"Converted:   {n_converted}")
print(f"Skipped:     {n_skipped}")
print(f"Output dir:  {OUT_DIR.resolve()}")
