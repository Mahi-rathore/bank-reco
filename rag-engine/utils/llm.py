from groq import Groq
from config.settings import settings
settings.groq_api_key
client = Groq(api_key=settings.groq_api_key)
def generate_response(results, profile, user_query):
    try:
        context = ""

        for r in results:
            context += f"{r['product']}: {r['description']}\n"

        prompt = f"""
You are a financial advisor.

User Profile:
Age: {profile['age']}
Income: {profile['income']}
Goal: {profile['goal']}
Risk: {profile['risk']}

User Question:
{user_query}

Available Products:
{context}
do not answer out of this context
Explain best recommendations clearly and simply.
"""

        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ LLM Error: {str(e)}"