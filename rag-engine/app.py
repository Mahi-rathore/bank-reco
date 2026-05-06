import streamlit as st
import requests
import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# CONFIG
st.set_page_config(page_title="AI Bank Advisor", layout="wide")


# STYLE
st.markdown("""
<style>

/* Fix chat visibility */
.stChatMessage {
    background-color: #ffffff !important;
    color: #111 !important;
    
}

/* assistant message */
[data-testid="stChatMessageAssistant"] {
    background-color: #f1f5f9 !important;
    color: #111 !important;
}

/* user message */
[data-testid="stChatMessageUser"] {
    background-color: #dbeafe !important;
    color: #111 !important;
}

</style>
""", unsafe_allow_html=True)

# HEADER
st.title("🏦 AI Bank Advisor")
st.caption("Smart Financial Insights Dashboard")


# INPUT
col1, col2, col3, col4 = st.columns(4)

with col1:
    age = st.number_input("Age", 0, 100, 0)

with col2:
    income = st.number_input("Income", 0, 10000000, 0)

with col3:
    goal = st.selectbox("Goal", ["Saving", "Investment", "Loan", "Insurance"])

with col4:
    risk = st.selectbox("Risk", ["Low", "Medium", "High"])

profile = {
    "age": age,
    "income": income,
    "goal": goal,
    "risk": risk
}


# SCORE
def get_score(income, risk):
    if income == 0:
        return "—"
    score = income / 10000
    if risk == "High":
        score *= 1.5
    elif risk == "Low":
        score *= 0.8
    return round(score, 2)

score = get_score(income, risk)


# CARDS
c1, c2, c3 = st.columns(3)

c1.markdown(f'<div class="card">💰<h2>₹{income}</h2>Income</div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card">🎯<h2>{goal}</h2>Goal</div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card">⭐<h2>{score}</h2>Score</div>', unsafe_allow_html=True)


# MAIN GRID
left, mid, right = st.columns([1.2, 1, 1])


# INSIGHTS
with left:
    st.subheader("🧠 Insights")

    if income == 0:
        st.warning("Enter income")
    else:
        if goal == "Insurance":
            st.info("Health & Life insurance recommended.")
        elif risk == "Low":
            st.success("Safe strategy: FD & savings.")
        elif risk == "Medium":
            st.info("Balanced strategy: SIP & savings.")
        else:
            st.error("High risk: stocks & aggressive funds.")


#  AUTO RECOMMENDATIONS 
with mid:
    st.subheader("💳 AI Recommendations")

    if income == 0:
        st.warning("Enter income to get recommendations")
    else:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/ask/",
                json={
                    "query": "Recommend best financial products",
                    "age": age,
                    "income": income,
                    "goal": goal,
                    "risk": risk
                }
            )

            data = response.json()
            results = data.get("results", [])

            for r in results[:3]:  # show top 3
                st.markdown(
                    f'<div class="small-card"><b>{r["product"]}</b><br>{r["description"][:120]}</div>',
                    unsafe_allow_html=True
                )

        except:
            st.error("Backend not reachable")


#  CHART (RESTORED)

with right:
    st.subheader("📊 Breakdown")

    if income == 0:
        st.info("Enter income")
    else:
        import plotly.express as px

        spending = income * 0.6
        savings = income * 0.4

        fig = px.pie(
            names=["Spending", "Savings"],
            values=[spending, savings],
            hole=0.5
        )

        st.plotly_chart(fig, use_container_width=True)


# CHATBOT
st.subheader("💬 AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask your financial question...")

if user_query:

    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.markdown(user_query)

    response = requests.post(
        "http://127.0.0.1:8000/ask/",
        json={
            "query": user_query,
            "age": age,
            "income": income,
            "goal": goal,
            "risk": risk
        }
    )

    data = response.json()
    ai_answer = data.get("ai_answer", "No response")

    st.session_state.messages.append({"role": "assistant", "content": ai_answer})

    with st.chat_message("assistant"):
        st.markdown(ai_answer)
