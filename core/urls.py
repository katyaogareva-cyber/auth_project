from django.urls import path
from .views import (
    register,login,logout,me,
    users_list,user_detail,
    orders_list,order_detail,
    rules_list,rule_detail,
    change_password
)

urlpatterns = [
    path("register/", register),
    path("login/", login),
    path("logout/", logout),
    path("me/", me),

    path("users/", users_list),
    path("users/<int:user_id>/", user_detail),
    path("users/<int:user_id>/change-password/", change_password),

    path("orders/", orders_list),
    path("orders/<int:order_id>/", order_detail),

    path("rules/", rules_list),
    path("rules/<int:rule_id>/", rule_detail),

]
