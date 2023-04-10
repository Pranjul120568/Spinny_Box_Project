from django.urls import path
from spinny import views


urlpatterns = [
    path('register/', views.register_user.as_view()),
    path('getusers/', views.get_users.as_view()),
    path('getuser/', views.getuser.as_view()),
    path('login/', views.login_user.as_view()),
    path('logout/', views.logout_user.as_view()),
    path('box/<int:id>', views.box_request.as_view()),
    path('getbox/<int:pk>', views.getbox.as_view()),
]
