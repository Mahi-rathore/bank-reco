import streamlit as st
import sys
import os
import faiss
import pickle

# -----------------------------
# 🔥 Fix import path
# -----------------------------
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# -----------------------------
# 🔥 Logger
# -----------------------------
def log(msg):
    print(f"[LOG] {msg}")

log("App started")

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="AI Bank Advisor", layout="wide")
st.title("💳 AI Bank Product Recommendation System")

# -----------------------------
# Load RAG (FAISS + Data)
# -----------------------------
try:
    if "rag_ready" not in st.session_state:

        log("Loading FAISS index...")
        index = faiss.read_index("vector_store/faiss_index.bin")

        log("Loading texts...")
        with open("vector_store/texts.pkl", "rb") as f:
            texts = pickle.load(f)

        log("Loading data...")
        with open("vector_store/data.pkl", "rb") as f:
            data = pickle.load(f)

        st.session_state["index"] = index
        st.session_state["texts"] = texts
        st.session_state["data"] = data
        st.session_state["rag_ready"] = True

        log(f"Loaded {len(texts)} texts")
        log(f"Loaded {len(data)} data entries")
        log("RAG ready")

except Exception as e:
    st.error(f"❌ RAG Load Error: {e}")
    log(f"ERROR in loading RAG: {e}")
    st.stop()

# -----------------------------
# 🔹 FORM SECTION
# -----------------------------
st.subheader("Enter Your Details")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=18, max_value=100)
    income = st.number_input("Annual Income (₹)", min_value=0)

with col2:
    goal = st.selectbox("Goal", ["Saving", "Investment", "Loan", "Insurance"])
    risk = st.selectbox("Risk Level", ["Low", "Medium", "High"])

# Save profile
if st.button("Get Recommendations"):
    st.session_state["user_profile"] = {
        "age": age,
        "income": income,
        "goal": goal,
        "risk": risk
    }
    log("User profile saved")
    st.success("Profile saved! Now chat below 👇")

# -----------------------------
# 🔹 CHAT SECTION
# -----------------------------
st.subheader("💬 Chat with AI Advisor")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 🔥 CHAT INPUT
# -----------------------------
from utils.rag_pipeline import retrieve

user_input = st.chat_input("Type your message...")

if user_input:
    log(f"User input: {user_input}")

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    if "user_profile" in st.session_state:
        profile = st.session_state["user_profile"]

        try:
            # 🔥 Build query
            log("Building query with profile...")

            query = f"""
            Age: {profile['age']}
            Income: {profile['income']}
            Goal: {profile['goal']}
            Risk: {profile['risk']}
            Query: {user_input}
            """

            log("Running FAISS retrieval...")

            results = retrieve(
                query,
                st.session_state["index"],
                st.session_state["texts"],
                st.session_state["data"]
            )

            log(f"Retrieved {len(results)} results")

            # 🔥 PRINT RETRIEVED CHUNKS
            log("Printing retrieved chunks:")
            for i, r in enumerate(results):
                log(f"--- Result {i+1} ---")
                log(f"Product: {r.get('product', 'N/A')}")
                log(f"Description: {r.get('description', '')[:200]}")

            # 🔥 SHOW IN UI (VERY USEFUL)
            with st.expander("🔍 Retrieved Context"):
                for r in results:
                    st.write(f"**{r.get('product', 'N/A')}**")
                    st.write(r.get("description", ""))
                    st.write("---")

            # 🔥 LLM CALL
            try:
                from utils.llm import generate_response

                log("Calling LLM...")

                with st.spinner("🤖 Thinking..."):
                    response = generate_response(results, profile, user_input)

                log("LLM response generated")

            except Exception as e:
                log(f"LLM ERROR: {e}")

                response = "### 💡 Recommended Products:\n\n"
                for r in results:
                    response += f"**{r['product']}**\n{r['description']}\n\n"

                response += f"\n⚠️ LLM Error: {str(e)}"

        except Exception as e:
            log(f"ERROR during retrieval: {e}")
            response = f"❌ Error: {str(e)}"

    else:
        response = "⚠️ Please fill the form first 👆"

    # Save response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Display response
    with st.chat_message("assistant"):
        st.markdown(response)