import time
import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q

from stories.models import Story
from stories.puter_ai_service import puter_ai_generator
from users.models import UserProfile
from .serializers import (
    StorySerializer, StoryCreateSerializer, StoryListSerializer,
    UserProfileSerializer, UserSerializer
)

logger = logging.getLogger(__name__)

# Story generation is now handled by the AI service module

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_story(request):
    """Generate a new story based on user input using AI or fallback algorithm"""
    serializer = StoryCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        start_time = time.time()
        
        # Extract validated data
        keywords = serializer.validated_data['keywords']
        genre = serializer.validated_data['genre']
        length = serializer.validated_data['length']
        tone = serializer.validated_data['tone']
        
        try:
            # Check if we should force template generation (from frontend fallback)
            force_template = request.META.get('HTTP_X_FORCE_TEMPLATE') == 'true'
            
            if force_template:
                # Force template generation
                story_result = puter_ai_generator._generate_simple(keywords, genre, length, tone)
            else:
                # Generate story using AI service (with automatic fallback)
                story_result = puter_ai_generator.generate_story(keywords, genre, length, tone)
            
            generation_time = time.time() - start_time
            
            # Create story object
            story = Story.objects.create(
                user=request.user,
                keywords=keywords,
                genre=genre,
                length=length,
                tone=tone,
                content=story_result['content'],
                generation_time=generation_time,
                ai_model_used=story_result['ai_model_used']
            )
            
            # Update user stats
            if hasattr(request.user, 'profile'):
                request.user.profile.update_stats()
            
            # Return generated story with AI status indicator
            response_serializer = StorySerializer(story)
            response_data = response_serializer.data
            response_data['generation_method'] = story_result.get('generation_method', 'unknown')
            response_data['ai_powered'] = story_result['generation_method'] == 'ai'
            
            logger.info(f"Story generated for user {request.user.username} using {story_result['generation_method']} method")
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error generating story for user {request.user.username}: {e}")
            return Response(
                {'error': 'Story generation failed. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoryListView(generics.ListAPIView):
    """List all stories with filtering options"""
    serializer_class = StoryListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Story.objects.all()
        
        # Filter by user if authenticated
        if self.request.user.is_authenticated:
            user_filter = self.request.query_params.get('user', None)
            if user_filter == 'me':
                queryset = queryset.filter(user=self.request.user)
        
        # Filter by public stories for anonymous users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
            
        # Filter by genre
        genre = self.request.query_params.get('genre', None)
        if genre:
            queryset = queryset.filter(genre=genre)
            
        # Filter by favorites
        favorites = self.request.query_params.get('favorites', None)
        if favorites == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user, is_favorite=True)
        
        return queryset.order_by('-created_at')

class StoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a story"""
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Story.objects.filter(user=self.request.user)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_story(request, story_id):
    """Rate a story (1-5 stars)"""
    story = get_object_or_404(Story, id=story_id, user=request.user)
    rating = request.data.get('rating')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return Response(
            {'error': 'Rating must be an integer between 1 and 5'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    story.rating = rating
    story.save()
    
    # Update user profile stats
    if hasattr(request.user, 'profile'):
        request.user.profile.update_stats()
    
    return Response({'message': 'Story rated successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, story_id):
    """Toggle favorite status of a story"""
    story = get_object_or_404(Story, id=story_id, user=request.user)
    story.is_favorite = not story.is_favorite
    story.save()
    
    # Update user profile stats
    if hasattr(request.user, 'profile'):
        request.user.profile.update_stats()
    
    return Response({
        'message': f'Story {"added to" if story.is_favorite else "removed from"} favorites',
        'is_favorite': story.is_favorite
    })

@api_view(['GET'])
def public_stories(request):
    """Get public stories for the gallery"""
    stories = Story.objects.filter(is_public=True).order_by('-created_at')
    
    # Optional genre filter
    genre = request.query_params.get('genre', None)
    if genre:
        stories = stories.filter(genre=genre)
    
    serializer = StoryListSerializer(stories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def ai_status(request):
    """Check if AI service is available"""
    return Response({
        'ai_available': puter_ai_generator.is_available(),
        'model': 'claude-sonnet-4' if puter_ai_generator.is_available() else 'template-based',
        'status': 'ready' if puter_ai_generator.is_available() else 'fallback'
    })

# Phase 2 - Export functionality
from stories.export_service import export_service

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_story(request, story_id, format_type):
    """Export a single story in specified format"""
    story = get_object_or_404(Story, id=story_id, user=request.user)
    
    try:
        if format_type == 'txt':
            return export_service.export_story_txt(story)
        elif format_type == 'pdf':
            return export_service.export_story_pdf(story)
        elif format_type == 'html':
            return export_service.export_story_html(story)
        else:
            return Response(
                {'error': 'Invalid format. Supported formats: txt, pdf, html'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Export error for story {story_id} in format {format_type}: {e}")
        return Response(
            {'error': 'Export failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_multiple_stories(request):
    """Export multiple stories as a ZIP archive"""
    try:
        story_ids = request.data.get('story_ids', [])
        format_type = request.data.get('format', 'txt')
        
        if not story_ids:
            return Response(
                {'error': 'No story IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if format_type not in ['txt', 'pdf', 'html']:
            return Response(
                {'error': 'Invalid format. Supported formats: txt, pdf, html'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get stories owned by the user
        stories = Story.objects.filter(id__in=story_ids, user=request.user)
        
        if not stories.exists():
            return Response(
                {'error': 'No valid stories found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return export_service.export_multiple_stories_zip(stories, format_type)
        
    except Exception as e:
        logger.error(f"Multiple export error for user {request.user.username}: {e}")
        return Response(
            {'error': 'Export failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_user_collection(request):
    """Export all user stories as a collection"""
    format_type = request.query_params.get('format', 'txt')
    
    try:
        if format_type not in ['txt', 'pdf', 'html']:
            return Response(
                {'error': 'Invalid format. Supported formats: txt, pdf, html'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return export_service.export_user_collection(request.user, format_type)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Collection export error for user {request.user.username}: {e}")
        return Response(
            {'error': 'Export failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
