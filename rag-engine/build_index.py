import os
import pickle
import faiss

from utils.data_loader import load_all_data
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer



#  Logger
def log(msg):
    print(f"[LOG] {msg}")



#  BASE PATH FIX (IMPORTANT)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store")

log(f"Base directory: {BASE_DIR}")
log(f"Vector store path: {VECTOR_STORE_PATH}")



#  START
log("Starting index build process...")



#  Load Data
log("Loading JSON + PDF data...")

json_data, pdf_docs = load_all_data()

log(f"Loaded JSON items: {len(json_data)}")
log(f"Loaded PDF documents: {len(pdf_docs)}")



#  Chunk PDFs
log("Splitting PDF documents into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunked_docs = text_splitter.split_documents(pdf_docs)

log(f"Total PDF chunks created: {len(chunked_docs)}")



#  Prepare Texts
log("Preparing text data for embeddings...")

texts = []

# JSON data
for item in json_data:
    text = f"{item['product']} {item['description']} {item.get('best_for', '')}"
    texts.append(text)

log(f"JSON texts added: {len(json_data)}")

# PDF chunks
for doc in chunked_docs:
    texts.append(doc.page_content)

log(f"Total texts (JSON + PDF): {len(texts)}")



#  Create Embeddings 
log("Loading embedding model...")

model = SentenceTransformer('all-MiniLM-L6-v2')

log("Creating embeddings (this may take time)...")

embeddings = model.encode(texts)

log(f"Embeddings created with shape: {embeddings.shape}")



#  Create FAISS Index
log("Creating FAISS index...")

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

log(f"FAISS index created with {index.ntotal} vectors")



#  Save Files 
log("Saving vector store...")

os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "faiss_index.bin"))

with open(os.path.join(VECTOR_STORE_PATH, "texts.pkl"), "wb") as f:
    pickle.dump(texts, f)


# Combine data for mapping
combined_data = json_data + [
    {"product": "PDF Knowledge", "description": doc.page_content}
    for doc in chunked_docs
]

with open(os.path.join(VECTOR_STORE_PATH, "data.pkl"), "wb") as f:
    pickle.dump(combined_data, f)



log(" Index built and saved successfully!")