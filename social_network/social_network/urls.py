"""
URL configuration for social_network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# social_network/urls.py

from django.contrib import admin
from django.urls import path
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.LoginView.as_view(), name='home'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search_users, name='search-users'),
    path('search-page/', views.search_page, name='search-page'),
    path('send-friend-request/', views.send_friend_request, name='send-friend-request'),
    path('respond-friend-request/', views.respond_to_friend_request, name='respond-friend-request'),
    path('friends/', views.friends_list, name='list-friends'),
    path('pending-requests/', views.ListPendingRequestsView.as_view(), name='list-pending-requests'),
]
