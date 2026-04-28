import os

print("CHECK PATH:", os.path.abspath("../../rag-engine/vector_store"))
import os

print("CHECK PATH:", os.path.abspath("../../rag-engine/vector_store"))
import sys
import os
from django.http import JsonResponse
from .models import Product
import json
from django.views.decorators.csrf import csrf_exempt
from .llm import generate_response


# 👇 add rag-engine path
sys.path.append(os.path.abspath("../rag-engine"))
#
from utils.rag_pipeline import retrieve


# -----------------------------
# 🔹 Helper: Parse JSON safely
# -----------------------------
def parse_request_body(request):
    try:
        return json.loads(request.body)
    except:
        return None


# -----------------------------
# 🔹 RECOMMEND API (basic)
# -----------------------------
@csrf_exempt
def recommend(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST request allowed"},
            status=405
        )

    data = parse_request_body(request)

    if not data:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    income = data.get("income")
    goal = data.get("goal")

    if income is None or goal is None:
        return JsonResponse(
            {"error": "income and goal are required"},
            status=400
        )

    try:
        # 🔹 Filter products
        products = Product.objects.filter(
            category__iexact=goal,
            min_income__lte=income
        )

        result = [
            {
                "name": p.name,
                "category": p.category,
                "risk_level": p.risk_level,
                "description": p.description
            }
            for p in products
        ]

        return JsonResponse({"products": result})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# -----------------------------
# 🔹 ASK API (AI Chatbot 🔥)
# -----------------------------
@csrf_exempt
def ask(request):

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        age = data.get("age")
        income = data.get("income")
        goal = data.get("goal")
        risk = data.get("risk")
        query = data.get("query")

        if income is None or goal is None or query is None:
            return JsonResponse({"error": "Missing fields"}, status=400)

        # -----------------------------
        # 1️⃣ DB RESULTS
        # -----------------------------
        products = Product.objects.filter(
            category__iexact=goal,
            min_income__lte=income
        )

        db_results = [
            {
                "product": p.name,
                "description": p.description,
                "risk_level": p.risk_level
            }
            for p in products
        ]

        # -----------------------------
        # 2️⃣ RAG RESULTS (PDF)
        # -----------------------------
        rag_query = f"{goal} {risk} {query}"
        rag_results = retrieve(rag_query)

        # -----------------------------
        # 3️⃣ MERGE
        # -----------------------------
        all_results = db_results + rag_results

        # -----------------------------
        # 4️⃣ PROFILE
        # -----------------------------
        profile = {
            "age": age,
            "income": income,
            "goal": goal,
            "risk": risk
        }

        # -----------------------------
        # 5️⃣ LLM
        # -----------------------------
        ai_answer = generate_response(all_results, profile, query)

        return JsonResponse({
            "results": all_results,
            "ai_answer": ai_answer
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)