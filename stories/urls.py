from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_story_view, name='generate'),
    path('my-stories/', views.my_stories, name='my_stories'),
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),
    path('gallery/', views.public_gallery, name='gallery'),
    
    # Phase 2 - Collections
    path('collections/', views.collections, name='collections'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:collection_id>/edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:collection_id>/delete/', views.delete_collection, name='delete_collection'),
    path('move-to-collection/', views.move_to_collection, name='move_to_collection'),
    
    # Public gallery and story list  
    path('stories/', views.public_gallery, name='story_list'),
] 