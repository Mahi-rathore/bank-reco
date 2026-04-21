import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="AI Bank Advisor", layout="wide")
st.title("💳 AI Bank Product Advisor (RAG + LLM)")

# -----------------------------
# Upload PDF
# -----------------------------
uploaded_file = st.file_uploader("Upload Bank PDF", type="pdf")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # -----------------------------
    # Load PDF
    # -----------------------------
    loader = PyPDFLoader("temp.pdf")
    documents = loader.load()

    # -----------------------------
    # Chunking
    # -----------------------------
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs = text_splitter.split_documents(documents)

    # -----------------------------
    # Embeddings
    # -----------------------------
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # -----------------------------
    # Vector DB (FAISS)
    # -----------------------------
    vectorstore = FAISS.from_documents(docs, embeddings)

    # -----------------------------
    # Retriever
    # -----------------------------
    retriever = vectorstore.as_retriever()

    # -----------------------------
    # LLM (Free alternative)
    # -----------------------------
    llm = HuggingFaceHub(
        repo_id="google/flan-t5-base",
        model_kwargs={"temperature": 0.5}
    )

    # -----------------------------
    # RAG Chain
    # -----------------------------
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever
    )

    # -----------------------------
    # Chat UI
    # -----------------------------
    query = st.text_input("Ask a question:")

    if query:
        answer = qa_chain.run(query)
        st.write("### 🤖 Answer:")
        st.write(answer)