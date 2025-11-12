# --------------------------------------------------------------
# scraper_update.py – update existing posts
# --------------------------------------------------------------

import json, time, random
from pathlib import Path
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

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

# Map URLs to existing post files
url_to_file = {}
for f in OUT.glob("post_*.json"):
    try:
        data = json.load(open(f, encoding="utf-8"))
        url_to_file[data["url"]] = f
    except:
        continue

d = driver()

try:
    for url in visited_urls:
        if url not in url_to_file:
            print(f"No original file for: {url}")
            continue

        json_file = url_to_file[url]
        pid = json_file.stem.split("_")[1]
        txt_file = OUT / f"post_{pid}.txt"

        try:
            d.get(url)
            human_delay(2, 5)

            soup = BeautifulSoup(d.page_source, "lxml")
            doc_parts = []

            post_content = soup.find("div", class_=lambda x: x and "post" in x.lower())
            if post_content:
                doc_parts.append(post_content.get_text(" ", strip=True))

            comments = soup.find_all("div", class_=lambda x: x and "comment" in x.lower())
            for c in comments:
                doc_parts.append(c.get_text(" ", strip=True))

            doc_text = "\n".join(doc_parts)

            # Compare with old text
            if txt_file.exists():
                old_text = txt_file.read_text(encoding="utf-8")
                if old_text == doc_text:
                    print(f"No change: {pid}")
                    continue

            # Overwrite files
            txt_file.write_text(doc_text, encoding="utf-8")

            json_data = json.load(open(json_file, encoding="utf-8"))
            json_data["content"] = doc_text
            json_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

            print(f"Updated: {pid}")

        except Exception as e:
            print(f"Failed: {url} -> {e}")

finally:
    d.quit()
