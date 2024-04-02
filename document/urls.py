from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.HomePage, name='home'),
    path('query/', views.query, name='query'),
    path('sumdb', views.sumdb, name='sumdb'),
    path('similarity', views.groupdb, name='similarity'),
    path('upload', views.upload, name='upload'),
    path('manage', views.manage, name='manage'),
    path('delete/<id>',views.delete, name='delete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)