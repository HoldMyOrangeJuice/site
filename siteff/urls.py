"""siteff URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from MainApp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", start_page),
    path("adm/", admin_page),
    path("price/", price_page),
    path("items/", show_custom_item_page),
    path("adm/order_page/", admin_order_page),
    path("my_orders/", user_order_page),

    path("accounts/login/", login_page),
    path("accounts/register/", register_page),
    path("accounts/confirm/", confirmation_page),

    path("accounts/me/", user_page),
    path("accounts/me/chat/", chatView),

]
