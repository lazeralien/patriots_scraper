# --------------------------------------------------------------
# scraper_urls_only.py – patriots.win post URLs
# --------------------------------------------------------------

import json, time, random
from pathlib import Path
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

URL = "https://patriots.win/new"
TOTAL = 1200
OUT = Path("posts")
OUT.mkdir(exist_ok=True)

URL_FILE = OUT / "visited_urls.json"

def human_delay(min_sec=0.5, max_sec=2.0):
    time.sleep(random.uniform(min_sec, max_sec))

def driver():
    opts = uc.ChromeOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=opts)

def incremental_scroll(driver, steps=5, step_delay=1.0):
    for i in range(steps):
        driver.execute_script(f"window.scrollBy(0, {8000 // steps});")
        human_delay(step_delay, step_delay + 0.5)

# Load previously collected URLs
if URL_FILE.exists():
    with open(URL_FILE) as f:
        visited_urls = set(json.load(f))
else:
    visited_urls = set()

# Launch driver
print("Launching Chrome...")
d = driver()
d.get(URL)
human_delay(2, 4)

count = len(visited_urls)
scrolls_done = 0
max_scrolls = 1000

try:
    while count < TOTAL and scrolls_done < max_scrolls:
        soup = BeautifulSoup(d.page_source, "lxml")
        posts = soup.find_all("div", class_=lambda x: x and "post" in x.lower())

        new_posts = []
        for post in posts:
            pid = post.get("id") or post.get("data-index")
            link_tag = post.find("a")
            url = link_tag['href'] if link_tag and link_tag.get("href") else None
            if url and url.startswith("/p/"):
                full_url = f"https://patriots.win{url}"
                if full_url not in visited_urls:
                    visited_urls.add(full_url)
                    new_posts.append((pid, full_url))
                    count += 1
                    print(f"[{count:4d}] {full_url}")

        if not new_posts:
            print("No new posts yet. Scrolling feed...")
            incremental_scroll(d, steps=5, step_delay=0.8)
            scrolls_done += 1
            continue

        incremental_scroll(d, steps=5, step_delay=0.8)
        scrolls_done += 1

finally:
    with open(URL_FILE, "w") as f:
        json.dump(list(visited_urls), f)
    d.quit()

print(f"\nDone! {count} URLs saved in '{OUT}'")
