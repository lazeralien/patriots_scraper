# --------------------------------------------------------------
# add_timestamps.py – one-time fix for old post JSONs
# Adds "fetched_at" timestamps and removes empty "content" fields
# --------------------------------------------------------------

import json
from datetime import datetime
from pathlib import Path

OUT = Path("posts")

count_updated = 0
count_skipped = 0

for f in OUT.glob("post_*.json"):
    try:
        data = json.load(open(f, encoding="utf-8"))
        changed = False

        # --- Add fetched_at if missing ---
        if "fetched_at" not in data:
            # Use file's modified time as fallback
            ts = datetime.utcfromtimestamp(f.stat().st_mtime)
            data["fetched_at"] = ts.isoformat() + "Z"
            changed = True

        # --- Remove empty content field ---
        if "content" in data and not data["content"].strip():
            del data["content"]
            changed = True

        if changed:
            f.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"Updated: {f.name}")
            count_updated += 1
        else:
            count_skipped += 1

    except Exception as e:
        print(f"Failed to update {f.name}: {e}")

print(f"\n✅ Done. Updated {count_updated} files, skipped {count_skipped}.")
