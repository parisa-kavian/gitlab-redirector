#Library

from django.conf import settings
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from enum import Enum
from typing import Optional
import json
import pandas as pd


# Definition of error class

class Statuses(Enum):
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    FILE_NOT_FOUND = 1
    ENCODING_ERROR = 1001

class ErrorModel:
    def __init__(self, error_code: Statuses, message: str):
        self.error_code = error_code
        self.message = message

class Status:
    @staticmethod
    def get(status: Statuses) -> Optional[ErrorModel]:
        all_statuses = [
            ErrorModel(Statuses.OK, "OK"),
            ErrorModel(Statuses.BAD_REQUEST, "There is a bad request."),
            ErrorModel(Statuses.NOT_FOUND, "Not found error occurred!"),
            ErrorModel(Statuses.FILE_NOT_FOUND, "File Not found error occurred!"),
            ErrorModel(Statuses.CONFLICT, "Conflict error has occurred!"),
            ErrorModel(Statuses.INTERNAL_SERVER_ERROR, "An internal error has occurred"),
            ErrorModel(Statuses.ENCODING_ERROR, "An error occurred in coding")
        ]
        return next((e for e in all_statuses if e.error_code == status), None)

class RequestResult:
    def __init__(self, status_code: Statuses, status_message: str, data: object):
        self.status_code = status_code
        self.status_message = status_message
        self.data = data

class OperationResult:
    @staticmethod
    def set_status(status: Statuses, response: object, error=None):
        state = Status.get(status)
        return RequestResult(state.error_code, state.message, response)

def load_foods_data():
    try: 
        food_csv = pd.read_csv('C:\\Users\\add\\allergicaAPII\\apii\\RecipeMaterials.csv', index_col='recipe_id')   
        
        return OperationResult.set_status(Statuses.OK, food_csv)
    except FileNotFoundError:
        return OperationResult.set_status(Statuses.FILE_NOT_FOUND, "")
    except Exception as error:
        print(f"Error: {error}")  
        return OperationResult.set_status(Statuses.ENCODING_ERROR, str(error))
    
def suggest_recipes(desired_ingredients, allergic_ingredients):
    try:
        foods = load_foods_data()
        # print("$$$$$$$$$$$$$$$$$$$$",foods.status_code.value)
        # print("@@@@@@@@@@@@@@@@@@@@@",Statuses.OK.value)
        # print("comparing is ",Statuses.OK == foods.status_code)
        # print("comparing2 is ",Statuses.OK.value == foods.status_code.value)
        if foods.status_code != Statuses.OK:
            return foods

        num_suggestions = 15
        allergy_threshold = 0.000001
        foods.data['ingredients']=foods.data['ingredients'].apply(lambda x: x.replace('mt-', ''))
        vectorizer = TfidfVectorizer()
        ingredient_vectors = vectorizer.fit_transform(foods.data['ingredients'])
        desired_ingredients_list = [ingredient.strip().lower().replace('mt-', '') for ingredient in desired_ingredients.split(',')]
        allergic_ingredients_list = [ingredient.strip().lower().replace('mt-', '') for ingredient in allergic_ingredients.split(',')]
        desired_ingredients_vector = vectorizer.transform([' '.join(desired_ingredients_list)])
        allergic_ingredients_vector = vectorizer.transform([' '.join(allergic_ingredients_list)])
        

        desired_similarity_scores = cosine_similarity(desired_ingredients_vector, ingredient_vectors).flatten()
        allergic_similarity_scores = cosine_similarity(allergic_ingredients_vector, ingredient_vectors).flatten()

        eligible_recipes_mask = allergic_similarity_scores < allergy_threshold
        eligible_foods = foods.data.iloc[eligible_recipes_mask].copy() 
        eligible_foods['desired_similarity_score'] = desired_similarity_scores[eligible_recipes_mask]
        eligible_foods['matching_ingredient_count'] = eligible_foods['ingredients'].apply(lambda x: sum(ingredient in x for ingredient in desired_ingredients_list))
        sorted_suggested_recipes = eligible_foods.sort_values(by=['matching_ingredient_count', 'desired_similarity_score'], ascending=[False, False])
        recipe_ids = sorted_suggested_recipes.index.tolist()
        
        return OperationResult.set_status(Statuses.OK, recipe_ids[:num_suggestions])
    except Exception as error:
        print(f"Error: {error}")
        return OperationResult.set_status(Statuses.ENCODING_ERROR, error)

# Testing the function
# desired_ingredients = 'mt-eggplant,mt-garlic,mt-barberry,mt-apple,mt-raisins'
# allergic_ingredients = 'mt-celery,mt-banana' 
# suggested_recipes = suggest_recipes(desired_ingredients,allergic_ingredients)
# print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",suggested_recipes.data)
# print(suggested_recipes.status_message)

# http://127.0.0.1:8000/apii/suggest-food/?desired_ingredients=mt-garlic,mt-tomatoes,mt-eggplant&allergic_ingredients=mt-onion,mt-eggs


def api_result(desired_ingredients, allergic_ingredients):
    suggest_recipes_result = suggest_recipes(desired_ingredients, allergic_ingredients)
    status_message = suggest_recipes_result.status_message
    return {
        "statusCode": suggest_recipes_result.status_code.value,
        "data": suggest_recipes_result.data,
        "message": status_message,
    }
    