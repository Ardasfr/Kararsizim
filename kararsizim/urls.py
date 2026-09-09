from django.contrib import admin
from django.urls import path, include
from polls import views as poll_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', include('polls.urls', namespace='polls')),
    # Debug preview routes for custom error pages
    path('error/404/', poll_views.custom_404, name='preview_404'),
    path('error/500/', poll_views.custom_500, name='preview_500'),
    path('error/403/', poll_views.custom_403, name='preview_403'),
]

handler404 = 'polls.views.custom_404'
handler500 = 'polls.views.custom_500'
handler403 = 'polls.views.custom_403'
