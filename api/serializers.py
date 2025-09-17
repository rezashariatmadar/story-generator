from rest_framework import serializers
from django.contrib.auth.models import User
from stories.models import Story
from users.models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'favorite_genre', 'preferred_length', 'preferred_tone', 
                 'stories_generated', 'favorite_stories_count', 'average_rating', 
                 'created_at', 'updated_at']
        read_only_fields = ['stories_generated', 'favorite_stories_count', 
                           'average_rating', 'created_at', 'updated_at']

class StorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    word_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Story
        fields = ['id', 'user', 'title', 'keywords', 'genre', 'length', 'tone', 
                 'content', 'created_at', 'updated_at', 'is_public', 'is_favorite', 
                 'rating', 'generation_time', 'ai_model_used', 'word_count']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'generation_time', 
                           'ai_model_used', 'word_count']

class StoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new stories - only includes input fields"""
    
    class Meta:
        model = Story
        fields = ['keywords', 'genre', 'length', 'tone']
        
    def validate_keywords(self, value):
        if not value.strip():
            raise serializers.ValidationError("Keywords cannot be empty")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Keywords must be at least 3 characters long")
        return value.strip()

class StoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing stories"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    word_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Story
        fields = ['id', 'title', 'keywords', 'genre', 'length', 'tone', 
                 'created_at', 'is_public', 'is_favorite', 'rating', 
                 'user_username', 'word_count'] 