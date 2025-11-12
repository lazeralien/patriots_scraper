# --------------------------------------------------------------
# scraper_update.py – update existing posts (least recently updated first)
# --------------------------------------------------------------

import json, time, random
from pathlib import Path
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime

OUT = Path("posts")
VISITED_FILE = OUT / "visited_urls.json"

def human_delay(min_sec=0.5, max_sec=2.0):
    time.sleep(random.uniform(min_sec, max_sec))

def driver():
    opts = uc.ChromeOptions()
    # opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=opts)

# Load visited URLs
if VISITED_FILE.exists():
    with open(VISITED_FILE) as f:
        visited_urls = set(json.load(f))
else:
    raise FileNotFoundError("visited_urls.json not found.")

# Map URLs to existing post files and track last fetched
url_to_file = {}
urls_with_time = []
for f in OUT.glob("post_*.json"):
    try:
        data = json.load(open(f, encoding="utf-8"))
        url = data["url"]
        url_to_file[url] = f
        fetched_at = data.get("fetched_at")
        if fetched_at:
            ts = datetime.fromisoformat(fetched_at.replace("Z", ""))
        else:
            ts = datetime.min  # treat missing as very old
        urls_with_time.append((ts, url))
    except:
        continue

# Sort URLs by oldest fetched first
urls_sorted = [u for _, u in sorted(urls_with_time)]

d = driver()

try:
    for url in urls_sorted:
        json_file = url_to_file.get(url)
        if not json_file:
            print(f"No original file for: {url}")
            continue

        pid = json_file.stem.split("_")[1]
        txt_file = OUT / f"post_{pid}.txt"

        try:
            d.get(url)
            human_delay(2, 5)

            soup = BeautifulSoup(d.page_source, "lxml")
            doc_parts = []

            # Post content
            post_content = soup.find("div", class_=lambda x: x and "post" in x.lower())
            if post_content:
                doc_parts.append(post_content.get_text(" ", strip=True))

            # Comments
            comments = soup.find_all("div", class_=lambda x: x and "comment" in x.lower())
            for c in comments:
                doc_parts.append(c.get_text(" ", strip=True))

            doc_text = "\n".join(doc_parts).strip()

            # Deduplicate lines
            lines = doc_text.splitlines()
            seen_lines = set()
            unique_lines = []
            for line in lines:
                l = line.strip()
                if l and l not in seen_lines:
                    seen_lines.add(l)
                    unique_lines.append(line)
            doc_text = "\n".join(unique_lines)

            # Compare with old text
            if txt_file.exists():
                old_text = txt_file.read_text(encoding="utf-8")
                if old_text == doc_text:
                    print(f"No change: {pid}")
                    continue

            # Overwrite text file
            txt_file.write_text(doc_text, encoding="utf-8")

            # Update JSON
            json_data = json.load(open(json_file, encoding="utf-8"))
            json_data["fetched_at"] = datetime.utcnow().isoformat() + "Z"

            if doc_text:
                json_data["content"] = doc_text
            elif "content" in json_data:
                del json_data["content"]

            json_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

            print(f"Updated: {pid}")

        except Exception as e:
            print(f"Failed: {url} -> {e}")

finally:
    d.quit()
