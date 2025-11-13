This scraper is designed specifically for patriots.win. This site is a custom made site so the scrapers will not be useable on other sites.

Workflow:

# 1. Collect the URLs
python scraper_urls_only.py 
# 2. Fetch posts & comments, creating the .txt and .json files
python scraper_fetch_posts.py
# 3. Update URLs and updates teh .txt and .json
python scraper_udpate.py
