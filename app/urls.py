# from django.urls import path
# from .views import UserManagementView

# user_view = UserManagementView()

# urlpatterns = [
#     path('navbar/', user_view.navbar, name='navbar'),

#     path('', user_view.index, name='index'),
#     path('home',user_view.home,name='home'),
#     path('about/', user_view.about, name='about'),
#     path('error/', user_view.error, name='error'),
#     path('feature/', user_view.feature, name='feature'),
#     path('service/', user_view.service, name='service'),
#     path('team/', user_view.team, name='team'),
#     path('testimonial/', user_view.testimonial, name='testimonial'),
#     path('appointment/', user_view.appoinment, name='appoinment'),
#     path('contact/', user_view.contact, name='contact'),
#     path('register/', user_view.register, name='register'),
#     path('verify/<uuid:token>/', user_view.verify_email, name='verify_email'),
#     path('login/', user_view.login, name='login'),
#     path('update-profile/', user_view.update_profile, name='update_profile'),
#     path('logout/', user_view.logout, name='logout'),
#     path('admin-dashboard/', user_view.admin_dashboard, name='admin_dashboard'),
#     path('delete-user/<int:id>/', user_view.delete_user, name='delete_user'),
#     path('forgot-password/', user_view.forgot_password_view, name='forgot_password'),
#     path('reset-password/<uuid:token>/', user_view.reset_password_view, name='reset_password'),
#     path('refresh-captcha/', user_view.refresh_captcha, name='refresh_captcha'),
#     path('get-districts/', user_view.get_districts, name='get_districts'),
# ]


from django.urls import path
from .views import UserManagementView

user_view = UserManagementView()

urlpatterns = [
    # AJAX specific endpoints
    path('navbar/', user_view.navbar, name='navbar'),
    path('refresh-captcha/', user_view.refresh_captcha, name='refresh_captcha'),
    path('get-districts/', user_view.get_districts, name='get_districts'),

    # Auth and profile POST handlers
    path('verify/<uuid:token>/', user_view.verify_email, name='verify_email'),
    path('logout/', user_view.logout, name='logout'),
    path('delete_user/<int:user_id>/', user_view.delete_user, name='delete_user'),
    path('reset-password/<uuid:token>/', user_view.reset_password_view, name='reset_password'),

    # Catch-all for SPA routes
    path('<str:page>/', user_view.spa_router, name='spa_router'),
    path('', user_view.spa_router, name='index'),  # Default route
]
