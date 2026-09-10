from django.urls import path
from . import views

app_name = 'wheels'

urlpatterns = [
    path('', views.wheel_list, name='list'),
    path('create/', views.wheel_create, name='create'),
    path('<uuid:wheel_id>/', views.wheel_detail, name='detail'),
    path('<uuid:wheel_id>/spin/', views.wheel_spin_record, name='spin_record'),
    path('<uuid:wheel_id>/delete/', views.wheel_delete, name='delete'),
]
