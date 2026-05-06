from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_response(results, profile, user_query):
    try:
        context = ""

        for r in results:
            context += f"{r['product']}: {r['description']}\n"

        prompt = f"""
You are a financial advisor.

User Profile:
Age: {profile.get('age')}
Income: {profile.get('income')}
Goal: {profile.get('goal')}
Risk: {profile.get('risk')}

User Question:
{user_query}

Available Products:
{context}

Recommend best products clearly.
"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ LLM Error: {str(e)}"