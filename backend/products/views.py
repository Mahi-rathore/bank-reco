from django.http import JsonResponse
from .models import Product
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def recommend(request):

    # ❌ Only POST allowed
    if request.method != "POST":
        return JsonResponse({"error": "Only POST request allowed"}, status=400)

    try:
        data = json.loads(request.body)

        income = data.get("income")
        goal = data.get("goal")

        # ❌ proper validation
        if income is None or goal is None:
            return JsonResponse(
                {"error": "income and goal are required"},
                status=400
            )

        # ✅ case-insensitive filtering
        products = Product.objects.filter(
            category__iexact=goal,
            min_income__lte=income
        )

        # ❌ agar kuch match nahi hua
        if not products.exists():
            return JsonResponse({
                "message": "No matching products found",
                "products": []
            })

        # ✅ clean + LLM ready response
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

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)