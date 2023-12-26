from django.urls import path
from . import views

urlpatterns = [
    path('suggest-food/', views.suggest_food, name='suggest_food'),
]