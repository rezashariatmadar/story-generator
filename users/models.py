from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # User preferences
    favorite_genre = models.CharField(max_length=20, blank=True, 
                                    choices=[
                                        ('fantasy', 'Fantasy'),
                                        ('sci_fi', 'Science Fiction'),
                                        ('romance', 'Romance'),
                                        ('horror', 'Horror'),
                                        ('mystery', 'Mystery'),
                                        ('adventure', 'Adventure'),
                                        ('drama', 'Drama'),
                                        ('comedy', 'Comedy'),
                                    ])
    preferred_length = models.CharField(max_length=10, blank=True,
                                      choices=[
                                          ('short', 'Short'),
                                          ('medium', 'Medium'),
                                          ('long', 'Long'),
                                      ])
    preferred_tone = models.CharField(max_length=15, blank=True,
                                    choices=[
                                        ('happy', 'Happy'),
                                        ('dark', 'Dark'),
                                        ('humorous', 'Humorous'),
                                        ('dramatic', 'Dramatic'),
                                        ('mysterious', 'Mysterious'),
                                        ('romantic', 'Romantic'),
                                    ])
    
    # Statistics
    stories_generated = models.IntegerField(default=0)
    favorite_stories_count = models.IntegerField(default=0)
    average_rating = models.FloatField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_stats(self):
        """Update user statistics based on their stories"""
        from stories.models import Story
        
        user_stories = Story.objects.filter(user=self.user)
        self.stories_generated = user_stories.count()
        self.favorite_stories_count = user_stories.filter(is_favorite=True).count()
        
        # Calculate average rating
        rated_stories = user_stories.filter(rating__isnull=False)
        if rated_stories.exists():
            self.average_rating = rated_stories.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating']
        
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
