from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('add/', views.add_position_view, name='add_position'),
    path('delete/<int:pk>/', views.delete_position_view, name='delete_position'),
]