from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Story(models.Model):
    GENRE_CHOICES = [
        ('fantasy', 'Fantasy'),
        ('sci_fi', 'Science Fiction'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('mystery', 'Mystery'),
        ('adventure', 'Adventure'),
        ('drama', 'Drama'),
        ('comedy', 'Comedy'),
    ]
    
    LENGTH_CHOICES = [
        ('short', 'Short (100-300 words)'),
        ('medium', 'Medium (300-600 words)'),
        ('long', 'Long (600-1000 words)'),
    ]
    
    TONE_CHOICES = [
        ('happy', 'Happy'),
        ('dark', 'Dark'),
        ('humorous', 'Humorous'),
        ('dramatic', 'Dramatic'),
        ('mysterious', 'Mysterious'),
        ('romantic', 'Romantic'),
    ]
    
    # User and basic info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=200, blank=True)
    collection = models.ForeignKey('StoryCollection', on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name='stories',
                                 help_text="Optional collection/folder")
    
    # Input parameters
    keywords = models.CharField(max_length=500, help_text="Keywords for story generation")
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='fantasy')
    length = models.CharField(max_length=10, choices=LENGTH_CHOICES, default='short')
    tone = models.CharField(max_length=15, choices=TONE_CHOICES, default='happy')
    
    # Generated content
    content = models.TextField(help_text="Generated story content")
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False, help_text="Make story public in gallery")
    is_favorite = models.BooleanField(default=False, help_text="User marked as favorite")
    rating = models.IntegerField(null=True, blank=True, help_text="User rating 1-5")
    
    # AI generation metadata
    generation_time = models.FloatField(null=True, blank=True, help_text="Time taken to generate in seconds")
    ai_model_used = models.CharField(max_length=100, default='gpt-3.5-turbo')
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title or 'Untitled'} by {self.user.username}"
        
    def save(self, *args, **kwargs):
        # Auto-generate title if not provided
        if not self.title and self.content:
            # Take first 50 chars as title
            self.title = self.content[:50] + "..." if len(self.content) > 50 else self.content
        super().save(*args, **kwargs)
        
    @property
    def word_count(self):
        return len(self.content.split()) if self.content else 0

class StoryCollection(models.Model):
    """
    Collections/folders for organizing stories
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100, help_text="Collection name")
    description = models.TextField(blank=True, help_text="Optional description")
    color = models.CharField(max_length=7, default='#6f42c1', help_text="Collection color (hex)")
    icon = models.CharField(max_length=50, default='fas fa-folder', help_text="FontAwesome icon class")
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False, help_text="Default collection for new stories")
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    @property
    def story_count(self):
        return self.stories.count()
    
    @property
    def total_words(self):
        return sum(story.word_count for story in self.stories.all())
    
    @property
    def average_rating(self):
        rated_stories = self.stories.filter(rating__isnull=False)
        if rated_stories.exists():
            return rated_stories.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return None
    
    def get_genre_distribution(self):
        """Get distribution of genres in this collection"""
        genres = {}
        for story in self.stories.all():
            genre = story.get_genre_display()
            genres[genre] = genres.get(genre, 0) + 1
        return genres

# Signal to create default collection for new users
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_default_collection(sender, instance, created, **kwargs):
    """Create a default 'My Stories' collection for new users"""
    if created:
        StoryCollection.objects.create(
            user=instance,
            name="My Stories",
            description="Your personal story collection",
            color="#6f42c1",
            icon="fas fa-book",
            is_default=True
        )
