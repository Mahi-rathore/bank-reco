import faiss
import pickle
import os
import numpy as np
from utils.embeddings import embed_text

# -----------------------------
# 🔥 CORRECT PATH (VERY IMPORTANT)
# -----------------------------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../vector_store")
)

print("👉 USING VECTOR STORE FROM:", BASE_DIR)

# -----------------------------
# 🔥 LOAD FILES
# -----------------------------
index = faiss.read_index(os.path.join(BASE_DIR, "faiss_index.bin"))

with open(os.path.join(BASE_DIR, "texts.pkl"), "rb") as f:
    texts = pickle.load(f)

with open(os.path.join(BASE_DIR, "data.pkl"), "rb") as f:
    data = pickle.load(f)

print("👉 INDEX SIZE:", index.ntotal)


# -----------------------------
# 🔥 RETRIEVE FUNCTION
# -----------------------------
def retrieve(query, top_k=3):

    print("👉 QUERY:", query)

    # convert to embedding
    query_vector = embed_text(query)

    # ensure numpy array (important)
    query_vector = np.array(query_vector)

    # search
    D, I = index.search(query_vector, top_k)

    print("👉 INDICES:", I)

    results = []

    for idx in I[0]:
        if idx < len(data):
            item = data[idx]

            results.append({
                "product": item.get("product", "PDF Info"),
                "description": item.get("description", texts[idx])
            })

    print("👉 RETRIEVED:", results)

    return results