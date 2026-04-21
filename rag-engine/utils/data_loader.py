import json
import os
from langchain_community.document_loaders import PyPDFLoader

def load_json():
    with open("data/bank_products.json", "r") as f:
        return json.load(f)

def load_pdfs():
    pdf_folder = "data/pdfs"
    documents = []

    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_folder, file))
            docs = loader.load()
            documents.extend(docs)

    return documents

def load_all_data():
    json_data = load_json()
    pdf_docs = load_pdfs()

    return json_data, pdf_docs