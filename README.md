This scraper is designed specifically for patriots.win. This site is a custom made site so the scrapers will not be useable on other sites.

Workflow:

# 1. Collect the URLs
python scraper_urls_only.py 
# 2. Fetch posts & comments, creating the .txt and .json files
python scraper_fetch_posts.py
# 3. Update URLs and updates teh .txt and .json
python scraper_udpate.py
# Additional
Multiple scripts were run to analyze and evaluate


# Report

Forum Search Evaluation Report
Project Overview
This project aimed to evaluate and improve search functionality for a niche forum, patriots.win, by implementing a small information retrieval system using BM25. The built-in search on the forum often misses relevant threads, especially for complex or niche queries, so this project explores whether BM25 can provide more accurate and relevant results.
The workflow was as follows:
    1. Data Collection: Using a custom scraper, forum threads (posts and comments) were collected. Each thread was treated as a single document.
    2. Indexing: The posts were preprocessed and indexed with Lucene via Pyserini, enabling BM25 retrieval.
    3. Querying: A set of 7 test queries was selected. For each query, the top results were retrieved using BM25.
    4. Evaluation: Relevance was manually annotated, and standard information retrieval metrics such as NDCG@10 and Precision@10 were calculated. Additionally, the same queries were run on the forum’s native search engine for comparison.

Methodology
Data Collection
    • Threads were scraped using a headless browser with undetected_chromedriver.
    • Post content and all comments were concatenated into a single document per thread.
    • Each document was saved as a JSON file containing the thread ID and URL, and later indexed for retrieval.
Indexing
    • Pyserini was used to create a Lucene index of the forum posts.
    • BM25 parameters were tuned (k1 = 2.0, b = 0.8) for relevance ranking.
    • Each post was treated as a document, and the URL served as an identifier to map results back to the original forum thread.
Queries and Relevance Judgments
    • Seven queries were selected based on recent forum topics:
        1. Government shutdown update
        2. Justice Department / Pam Bondi
        3. Utah congress map
        4. Illegal immigration
        5. Pipe bomber / Capitol police
        6. Communism and socialism
        7. Capitalism
    • Relevance judgments were manually created for the retrieved posts (Cranfield-style evaluation).
    • Metrics computed:
        ○ NDCG@10: Measures ranking quality, emphasizing highly relevant posts at the top.
        ○ Precision@10: Fraction of relevant posts in the top 10 results.

Results
Query	Average BM25 Score	Website Retrieval
Query 1: government shutdown update	4.7313	None
Query 2: justice department pam bondi	6.9098	None
Query 3: utah congress map	5.6365	None
Query 4: illegal immigration	2.8880	Many
Query 5: pipe bomber capitol police	10.5368	One
Query 6: communism and socialism	2.6193	Many
Query 7: capitalism	2.2738	Many
    • Overall metrics across all queries:
        ○ NDCG@10: 0.3586
        ○ Precision@10: 0.1571
Observations
    • The forum’s native search engine failed to retrieve relevant results for 3 of 7 queries.
    • For query 5, only a single post was returned, likely due to the topic being highly specific and recent.
    • BM25 retrieval returned more relevant posts consistently, even for queries where the forum search failed.
    • Query 5 achieved the highest average score, possibly because posts about the event remained on topic and were easier to rank.
    • Query 6 and 7 returned many posts, reflecting broader topics with more discussion and varying relevance.

Limitations
    • The scraper only pulled posts from the top and front pages, which are biased toward popular or recent threads. The forum itself has years of posts that were not included in this evaluation.
    • The evaluation set is small (7 queries), so metrics may not fully capture the general effectiveness of BM25 vs the forum search.
    • Manual relevance judgments are subjective and could be refined with more annotators or larger query sets.

Conclusion
    • BM25 clearly improves retrieval for queries where the forum’s native search fails or is inconsistent.
    • For queries with a narrow topical focus, BM25 can rank relevant threads higher than the website search.
    • Overall, implementing BM25 over a custom forum index provides more relevant, up-to-date, and content-rich results, demonstrating the utility of traditional information retrieval methods for niche forums.
Next Steps
    1. Expand the corpus to include all threads for a more complete evaluation.
    2. Increase the number of queries and relevance judgments to improve statistical significance.
    3. Experiment with query expansion or relevance feedback to further improve ranking.
Compare BM25 with other retrieval models such as language models with smoothing for a more advanced evaluation.