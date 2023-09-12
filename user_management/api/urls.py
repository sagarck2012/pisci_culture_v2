from django.urls import path
from .views import MyTokenObtainPairView, create_user, senso_login, senso_logout, logout
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create/', create_user, name='create_user'),
    path('login/', senso_login, name='senso_login'),
    # path('logout/', senso_logout, name='senso_logout'),
    path('logout/', logout, name='logout'),
]
