from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.poll_feed, name='feed'),
    path('poll/create/', views.poll_create, name='create'),
    path('poll/<uuid:poll_id>/', views.poll_detail, name='detail'),
    path('poll/<uuid:poll_id>/vote/', views.poll_vote, name='vote'),
    path('poll/<uuid:poll_id>/results/', views.poll_results, name='results'),
    path('poll/<uuid:poll_id>/delete/', views.poll_delete, name='delete'),
]
