from django.urls import path
from . import views

urlpatterns = [
    path('', views.favorites_list_view, name='favorites'),
    path('toggle/<str:symbol>/', views.toggle_favorite, name='toggle_favorite'),
    path('delete/<str:symbol>/', views.delete_favorite, name='delete_favorite'),
]