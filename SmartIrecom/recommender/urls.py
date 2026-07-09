"""
URL configuration for the recommender app.

Maps the root URL to the search view, making it the landing page.
"""

from django.urls import path

from . import views

app_name = 'recommender'

urlpatterns = [
    path('', views.search_view, name='search'),
]
