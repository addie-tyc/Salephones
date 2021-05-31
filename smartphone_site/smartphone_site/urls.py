"""smartphone_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from smartphone_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('smartphone-smartprice/home', views.home_page),
    path('smartphone-smartprice/detail/<str:title>/<int:storage>', views.detail_page),
    path('smartphone-smartprice/signup', views.SignUpView.as_view(), name="signup"),
    path('smartphone-smartprice/login', views.LoginView.as_view(), name="login"),
    path('smartphone-smartprice/logout', views.LogoutView.as_view(), name="logout"),
    path('smartphone-smartprice/sale', views.SaleView.as_view(), name="sale"),
    path('api/v1/home', views.PttHomeView.as_view()),
    path('api/v1/detail', views.PttDetailView.as_view()),
    path('api/v1/comments', views.CommentsView.as_view()),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
