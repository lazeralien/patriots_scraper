# --------------------------------------------------------------
# scraper_fetch_posts.py – fetch posts + comments
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
    # opts.add_argument("--headless")  # optional
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=opts)

# Load URLs
if VISITED_FILE.exists():
    with open(VISITED_FILE) as f:
        urls = set(json.load(f))
else:
    raise FileNotFoundError("visited_urls.json not found. Run scraper_urls_only.py first.")

d = driver()

try:
    for url in urls:
        try:
            d.get(url)
            human_delay(1, 3)

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

            doc_text = "\n".join(doc_parts)

            # Create post ID from URL
            pid = url.split("/p/")[1].split("/")[0]

            # Write txt and json
            txt_file = OUT / f"post_{pid}.txt"
            json_file = OUT / f"post_{pid}.json"

            txt_file.write_text(doc_text, encoding="utf-8")
            json_file.write_text(json.dumps({
                "id": pid,
                "url": url,
                "content": doc_text
            }, indent=2), encoding="utf-8")

            print(f"Saved: {pid}")

        except Exception as e:
            print(f"Failed: {url} -> {e}")

finally:
    d.quit()
