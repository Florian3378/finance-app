from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('transaction/add/', views.add_transaction_view, name='add_transaction'),
    path('position/<int:pk>/', views.position_detail_view, name='position_detail'),
    path('transaction/<int:pk>/delete/', views.delete_transaction_view, name='delete_transaction'),
]