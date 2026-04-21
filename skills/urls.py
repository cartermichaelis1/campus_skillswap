from django.urls import path
from . import views

urlpatterns = [
    # Home / landing page
    path('', views.home, name='home'),

    # Skill browsing (Extension 1: search is built into this view)
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/<int:pk>/', views.skill_detail, name='skill_detail'),

    # Skill management (create, edit, delete) — login required
    path('skills/create/', views.skill_create, name='skill_create'),
    path('skills/<int:pk>/edit/', views.skill_edit, name='skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),

    # Extension 3: Review submission
    path('skills/<int:pk>/review/', views.add_review, name='add_review'),

    # User dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Registration (login/logout come from django.contrib.auth.urls)
    path('accounts/register/', views.register, name='register'),
]
