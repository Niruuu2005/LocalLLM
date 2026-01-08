from django.urls import path
from .views import chat_view, register_view, login_view, logout_view, pricing_view

urlpatterns = [
    path('', chat_view, name='chat'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('pricing/', pricing_view, name='pricing'),
]
