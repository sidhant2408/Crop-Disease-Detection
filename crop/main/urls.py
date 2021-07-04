from django.contrib import admin
from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.homepage, name = "homepage"),
    path('desease/<str:pk>', views.desease, name = "desease"),
    path('search/', views.search, name = "search"),
    path('voiceSearch/', views.voice_search, name="search"),
    path('about/', views.about, name="about"),
    path('scrap_desease/<str:pk>', views.desease_scrap, name="desease_scrap"),
    path('camera_search/', views.camera_search, name="camera_search"),
    path('camera_search/camera_search', views.camera_search, name="camera_search"),
    path('register/', views.register, name="register"),
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logout_request, name="logout"),
    path('update_database/', views.update_database, name="update_database"),
    path('change_database/<str:pk>', views.change_database, name="change_database"),
    path('delete_database/<str:pk>', views.delete_database, name="delete_database"),
    path('user', views.user_page, name = "user"),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)