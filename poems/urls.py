from django.urls import path
from . import views

urlpatterns = [
    # Auth (combined animated page)
    path('auth/', views.auth_view, name='auth'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Email verification
    path('verify-email/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),

    # Password reset
    path('forgot-password/', views.password_reset_request_view, name='password_reset'),
    path('forgot-password/done/', views.password_reset_request_view, name='password_reset_done'),
    path('reset-password/<str:uidb64>/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),

    # Feed
    path('', views.feed_view, name='feed'),

    # Poems
    path('poem/new/', views.create_poem_view, name='create_poem'),
    path('poem/<int:pk>/', views.poem_detail_view, name='poem_detail'),
    path('poem/<int:pk>/edit/', views.edit_poem_view, name='edit_poem'),
    path('poem/<int:pk>/delete/', views.delete_poem_view, name='delete_poem'),
    path('poem/<int:pk>/like/', views.toggle_like_view, name='toggle_like'),
    path('poem/<int:pk>/comment/', views.ajax_comment_view, name='ajax_comment'),


    # Profile
    path('profile/<int:username_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Direct Messages
    path('messages/', views.inbox_view, name='inbox'),
    path('messages/dm/<int:user_id>/start/', views.start_dm_view, name='start_dm'),
    path('messages/dm/<int:conv_id>/', views.dm_thread_view, name='dm_thread'),
    path('messages/dm/<int:conv_id>/poll/', views.dm_poll_view, name='dm_poll'),

    # Groups
    path('messages/groups/new/', views.create_group_view, name='create_group'),
    path('messages/groups/<int:group_id>/', views.group_chat_view, name='group_chat'),
    path('messages/groups/<int:group_id>/poll/', views.group_poll_view, name='group_poll'),
    path('messages/groups/<int:group_id>/add/', views.group_add_member_view, name='group_add_member'),
    path('messages/groups/<int:group_id>/leave/', views.group_leave_view, name='group_leave'),
]
