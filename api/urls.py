from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Story generation and management
    path('generate/', views.generate_story, name='generate_story'),
    path('stories/', views.StoryListView.as_view(), name='story_list'),
    path('stories/<int:pk>/', views.StoryDetailView.as_view(), name='story_detail'),
    path('stories/<int:story_id>/rate/', views.rate_story, name='rate_story'),
    path('stories/<int:story_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Public endpoints
    path('public/stories/', views.public_stories, name='public_stories'),
    path('ai-status/', views.ai_status, name='ai_status'),
    
    # Phase 2 - Export functionality
    path('stories/<int:story_id>/export/<str:format_type>/', views.export_story, name='export_story'),
    path('export/multiple/', views.export_multiple_stories, name='export_multiple'),
    path('export/collection/', views.export_user_collection, name='export_collection'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
] 