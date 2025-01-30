"""stock_project URL Configuration

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
from django.urls import path
from stock_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name="home"),
    path('questions/', views.questions, name="questions"),
    path('submit-answers/', views.submit_answers),
    path('recommended_vehicle/', views.recommended, name='recommended'),
    path('login/', views.login, name="login"),
    path('signup/', views.signup, name="signup"),
    path('signup_auth/', views.signup_auth,),
    path('login_auth/', views.login_auth),
    path('get-user/', views.get_user_info, name='get_user'),
]
