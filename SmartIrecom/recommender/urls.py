"""
URL configuration for the recommender app.

Maps the root URL to the search view, making it the landing page.
"""

from django.urls import path

from . import views

app_name = 'recommender'

urlpatterns = [
    path('wizard/', views.wizard_view, name='wizard'),
    path('', views.search_view, name='search'),
    path('evaluasi/', views.compare_view, name='compare'),
    path('evaluasi/multi-query/', views.multi_query_evaluation_view, name='multi_query_evaluation'),
]
