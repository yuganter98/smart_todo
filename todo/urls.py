from django.urls import path
from .views import TaskList, CategoryList, ContextEntryList, AISuggestions

urlpatterns = [
    path('tasks/', TaskList.as_view()),
    path('categories/', CategoryList.as_view()),
    path('context/', ContextEntryList.as_view()),
    path('ai/suggestions/', AISuggestions.as_view()),
]