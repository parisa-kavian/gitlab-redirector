

from django.http import JsonResponse
# from apii.try_except_without_ingr import api_result
from apii.yt import api_result
def suggest_food(request):
    desired_ingredients = request.GET.get('desired_ingredients', '')
    allergic_ingredients = request.GET.get('allergic_ingredients', '')
    recommendations = api_result(desired_ingredients,allergic_ingredients)
    print("recommendations", recommendations)
    return JsonResponse ({"statusCode": recommendations.get("statusCode", None),
        "data": recommendations.get("data", None),
        "message": recommendations.get("message", None)
    })


