def recommend_products(profile, data):
    results = []

    for item in data:
        if profile["risk"].lower() == item["risk"].lower():
            results.append(item)

    return results[:3]