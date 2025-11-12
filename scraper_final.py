# --------------------------------------------------------------
# scraper_final_idempotent_incremental_scroll.py – patriots.win posts + comments
# --------------------------------------------------------------

import json, time, random
from pathlib import Path
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

URL = "https://patriots.win/top"
TOTAL = 1200
OUT = Path("posts")
OUT.mkdir(exist_ok=True)

VISITED_FILE = OUT / "visited_urls.json"

def human_delay(min_sec=0.5, max_sec=2.0):
    """Sleep for a random time between min_sec and max_sec."""
    time.sleep(random.uniform(min_sec, max_sec))

def driver():
    opts = uc.ChromeOptions()
    # opts.add_argument("--headless")  # remove for debugging
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=opts)

def incremental_scroll(driver, steps=5, step_delay=1.0):
    """Scrolls down the page incrementally."""
    for i in range(steps):
        driver.execute_script(f"window.scrollBy(0, {8000 // steps});")
        human_delay(step_delay, step_delay + 0.5)

# --- Load previously scraped IDs ---
existing_files = set(f.stem.split("_")[1] for f in OUT.glob("post_*.txt"))
seen_ids = set(existing_files)

# --- Load previously visited URLs ---
if VISITED_FILE.exists():
    with open(VISITED_FILE) as f:
        visited_urls = set(json.load(f))
else:
    visited_urls = set()

# Launch driver
print("Launching Chrome...")
d = driver()
d.get(URL)
human_delay(2, 4)

count = len(seen_ids)
scrolls_done = 0
max_scrolls = 1000

try:
    while count < TOTAL and scrolls_done < max_scrolls:
        soup = BeautifulSoup(d.page_source, "lxml")

        # Find all post-like divs
        posts = soup.find_all("div", class_=lambda x: x and "post" in x.lower())
        new_posts = [p for p in posts if (p.get("id") or p.get("data-index")) not in seen_ids]

        if not new_posts:
            # Incremental scroll on main feed
            print("No new posts yet. Incrementally scrolling the feed...")
            incremental_scroll(d, steps=5, step_delay=0.8)
            human_delay(1, 2)
            scrolls_done += 1
            continue

        for post in new_posts:
            if count >= TOTAL:
                break

            pid = post.get("id") or post.get("data-index")
            seen_ids.add(pid)

            # Title & URL
            title_tag = post.find("h3")
            title = title_tag.get_text(strip=True) if title_tag else post.get_text(strip=True)[:100]

            link_tag = post.find("a")
            url = link_tag['href'] if link_tag and link_tag.get("href") else None

            if not url or not url.startswith("/p/"):
                # Skip non-posts
                continue

            full_url = f"https://patriots.win{url}"
            if full_url in visited_urls:
                print(f"Already visited URL: {full_url}")
                continue
            visited_urls.add(full_url)

            # --- Visit the post page ---
            try:
                d.get(full_url)
                human_delay(2, 5)

                post_soup = BeautifulSoup(d.page_source, "lxml")
                doc_parts = []

                # Post content
                post_content = post_soup.find("div", class_=lambda x: x and "post" in x.lower())
                if post_content:
                    doc_parts.append(post_content.get_text(" ", strip=True))

                # Comments
                comments = post_soup.find_all("div", class_=lambda x: x and "comment" in x.lower())
                for c in comments:
                    doc_parts.append(c.get_text(" ", strip=True))

                doc_text = "\n".join(doc_parts)

                # Save files
                Path(OUT / f"post_{pid}.txt").write_text(doc_text, encoding="utf-8")
                Path(OUT / f"post_{pid}.json").write_text(
                    json.dumps({
                        "id": pid,
                        "title": title,
                        "url": full_url,
                        "content": doc_text
                    }, indent=2),
                    encoding="utf-8"
                )

                count += 1
                print(f"[{count:3d}] {title[:70]}")

                # Persist visited URLs every 5 posts
                if count % 5 == 0:
                    with open(VISITED_FILE, "w") as f:
                        json.dump(list(visited_urls), f)

            except Exception as e:
                print(f"Could not open {full_url}: {e}")

            finally:
                # Return to main feed
                d.get(URL)
                human_delay(1.5, 3.0)
                # Incrementally scroll back down to last known scroll
                incremental_scroll(d, steps=scrolls_done + 1, step_delay=0.5)

        # Final incremental scroll after processing batch
        incremental_scroll(d, steps=5, step_delay=0.8)
        scrolls_done += 1

finally:
    # Save visited URLs on exit
    with open(VISITED_FILE, "w") as f:
        json.dump(list(visited_urls), f)
    d.quit()

print(f"\nDone! {count} posts saved in '{OUT}'")
