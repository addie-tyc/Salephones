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
import env

ssl_path = env.SSL_PATH

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', views.home_page, name="home"),
    path('detail/<str:title>/<int:storage>', views.detail_page),
    path('profile', views.profile_page),
    path('signup', views.SignUpView.as_view(), name="signup"),
    path('login', views.LoginView.as_view(), name="login"),
    path('logout', views.LogoutView.as_view(), name="logout"),
    path('sale', views.SaleView.as_view(), name="sale"),
    path('post/<int:id>', views.PostView.as_view()),
    path('api/v1/home', views.PttHomeView.as_view()),
    path('api/v1/table', views.PttTableView.as_view()),
    path('api/v1/price-graph', views.PttPriceGraphView.as_view()),
    path('api/v1/storage-graph', views.PttStorageGraphView.as_view()),
    path('api/v1/comments', views.CommentsView.as_view()),
    path('api/v1/profile', views.ProfileView.as_view()),
    path(ssl_path, views.get_ssl_file),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
