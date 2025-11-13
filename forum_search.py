# --------------------------------------------------------------
# forum_search.py — BM25 search + evaluation for forum threads
# --------------------------------------------------------------
import os, json, subprocess
from tqdm import tqdm
from pyserini.index.lucene import LuceneIndexReader
from pyserini.search.lucene import LuceneSearcher
import numpy as np

def build_index(input_dir, index_dir):
    if os.path.exists(index_dir) and os.listdir(index_dir):
        print(f"Index already exists at {index_dir}, skipping.")
        return
    cmd = [
        "python", "-m", "pyserini.index.lucene",
        "--collection", "JsonCollection",
        "--input", input_dir,
        "--index", index_dir,
        "--generator", "DefaultLuceneDocumentGenerator",
        "--threads", "2",
        "--storePositions", "--storeDocvectors", "--storeRaw"
    ]
    subprocess.run(cmd, check=True)

def search(searcher, queries, top_k=10):
    results = {}
    for i, query in enumerate(tqdm(queries, desc="Searching")):
        hits = searcher.search(query, k=top_k)
        results[str(i+1)] = [(hit.docid, hit.score) for hit in hits]
    return results

def compute_precision(results, qrels, k=10, threshold=1):
    precisions = []
    for qid, docs in results.items():
        if qid not in qrels:
            continue
        relevant = sum(qrels[qid].get(docid,0) >= threshold for docid,_ in docs[:k])
        precisions.append(relevant/k)
    return np.mean(precisions) if precisions else 0

def compute_ndcg(results, qrels, k=10):
    def dcg(rels): return sum(r/np.log2(i+2) for i,r in enumerate(rels[:k]))
    ndcgs = []
    for qid, docs in results.items():
        if qid not in qrels: continue
        rels = [qrels[qid].get(docid,0) for docid,_ in docs]
        idcg = dcg(sorted(qrels[qid].values(), reverse=True))
        if idcg>0: ndcgs.append(dcg(rels)/idcg)
    return np.mean(ndcgs) if ndcgs else 0

def load_qrels(qrels_file):
    qrels = {}
    with open(qrels_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 4:
                qid, _, docid, rel = parts  # ignore the second field
            elif len(parts) == 3:
                qid, docid, rel = parts
            else:
                raise Exception(f"Incorrect line: {line.strip()}")

            if qid not in qrels:
                qrels[qid] = {}
            qrels[qid][docid] = int(rel)
    return qrels


if __name__ == "__main__":
    corpus_dir = "processed_corpus/patriots_forum"
    index_dir = "indexes/patriots_forum"
    query_file = "data/forum_queries.txt"
    qrels_file = "qrels.txt"

    build_index(corpus_dir, index_dir)
    searcher = LuceneSearcher(index_dir)
    searcher.set_bm25(k1=1.5, b=0.75)

    queries = [q.strip() for q in open(query_file) if q.strip()]
    qrels = load_qrels(qrels_file)

    results = search(searcher, queries, top_k=10)
    ndcg = compute_ndcg(results, qrels)
    prec = compute_precision(results, qrels)

    print(f"NDCG@10 = {ndcg:.4f}, Precision@10 = {prec:.4f}")

    json.dump({"results": results, "NDCG": ndcg, "Precision": prec},
              open("results_forum.json", "w"), indent=2)
