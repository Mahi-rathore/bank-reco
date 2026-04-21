from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve(query, index, texts, data, top_k=3):
    query_embedding = model.encode([query])

    distances, indices = index.search(np.array(query_embedding), top_k)

    results = []
    for i in indices[0]:
        results.append(data[i])

    return results