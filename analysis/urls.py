from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('company/<str:symbol>/', views.company_view, name='company'),
]