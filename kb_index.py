# kb_index.py
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_vectorizer = None
_docs = []
_fnames = []
KB_DIR = "kb"

def _load_kb(kb_dir: str):
    """Load all .txt files from kb_dir."""
    global _docs, _fnames
    _docs, _fnames = [], []

    if not os.path.isdir(kb_dir):
        return

    for fname in sorted(os.listdir(kb_dir)):
        if fname.lower().endswith(".txt"):
            path = os.path.join(kb_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                _docs.append(f.read())
                _fnames.append(fname)

def build_index(kb_dir: str = "kb"):
    """Build TF-IDF index from kb_dir."""
    global _vectorizer
    _load_kb(kb_dir)

    if not _docs:
        _vectorizer = None
        print("KB empty — no docs found.")
        return

    _vectorizer = TfidfVectorizer(stop_words="english")
    _vectorizer.fit(_docs)

    print(f"KB built (TF-IDF) from folder: {kb_dir}")

def query_kb(query: str, top_k: int = 1, min_score: float = 0.12) -> str:
    """Return most relevant KB snippet, or empty string if too low score."""
    global _vectorizer, _docs

    if _vectorizer is None:
        build_index(KB_DIR)

    if not _docs or _vectorizer is None:
        return ""

    qv = _vectorizer.transform([query])
    dv = _vectorizer.transform(_docs)

    sims = cosine_similarity(qv, dv)[0]
    best_idx = int(sims.argmax())

    if sims[best_idx] < min_score:
        return ""

    return _docs[best_idx]
