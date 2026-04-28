from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')


#  Create embeddings (bulk)
def create_embeddings(json_data, pdf_docs):
    texts = []

    # JSON data
    for item in json_data:
        text = f"{item['product']} {item['description']} {item.get('best_for', '')}"
        texts.append(text)

    # PDF data
    for doc in pdf_docs:
        texts.append(doc.page_content)

    embeddings = model.encode(texts)

    return embeddings, texts


# Create FAISS index
def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return index


#  ADD THIS FUNCTION 
def embed_text(query):
    return model.encode([query])