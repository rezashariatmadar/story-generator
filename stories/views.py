from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import json

from .models import Story
from users.models import UserProfile
from .forms import StoryGenerationForm, UserProfileForm
from .models import StoryCollection
from .forms import StoryCollectionForm

def home(request):
    """Home page with story generation form"""
    form = StoryGenerationForm()
    recent_stories = Story.objects.filter(is_public=True).order_by('-created_at')[:6]
    
    context = {
        'form': form,
        'recent_stories': recent_stories,
    }
    return render(request, 'stories/home.html', context)

@login_required
def generate_story_view(request):
    """Generate a new story"""
    if request.method == 'POST':
        form = StoryGenerationForm(request.POST)
        if form.is_valid():
            # Get or create default collection for the user
            default_collection = StoryCollection.objects.filter(
                user=request.user, 
                is_default=True
            ).first()
            
            # If no default collection exists, create one
            if not default_collection:
                default_collection = StoryCollection.objects.create(
                    user=request.user,
                    name="My Stories",
                    description="Your personal story collection",
                    color="#6f42c1",
                    icon="fas fa-book",
                    is_default=True
                )
            
            return JsonResponse({'success': True, 'default_collection': default_collection.id})
    else:
        form = StoryGenerationForm()
        
        # Pre-fill with user preferences
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            form.initial = {
                'genre': profile.favorite_genre,
                'length': profile.preferred_length,
                'tone': profile.preferred_tone,
            }
    
    # Get user's collections for the dropdown
    collections = StoryCollection.objects.filter(user=request.user).order_by('name')
    
    context = {
        'form': form,
        'collections': collections
    }
    return render(request, 'stories/generate.html', context)

@login_required
def my_stories(request):
    """User's story history with advanced search and filtering"""
    stories = Story.objects.filter(user=request.user).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        stories = stories.filter(
            Q(title__icontains=search_query) |
            Q(keywords__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter options
    genre_filter = request.GET.get('genre')
    length_filter = request.GET.get('length')
    tone_filter = request.GET.get('tone')
    favorites_only = request.GET.get('favorites')
    ai_filter = request.GET.get('ai_generated')
    rating_filter = request.GET.get('rating')
    date_filter = request.GET.get('date_range')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Apply filters
    if genre_filter:
        stories = stories.filter(genre=genre_filter)
    if length_filter:
        stories = stories.filter(length=length_filter)
    if tone_filter:
        stories = stories.filter(tone=tone_filter)
    if favorites_only:
        stories = stories.filter(is_favorite=True)
    if ai_filter:
        if ai_filter == 'ai':
            stories = stories.exclude(ai_model_used='simple_algorithm')
        elif ai_filter == 'template':
            stories = stories.filter(ai_model_used='simple_algorithm')
    if rating_filter:
        if rating_filter == 'unrated':
            stories = stories.filter(rating__isnull=True)
        elif rating_filter == '5':
            stories = stories.filter(rating=5)
        elif rating_filter == '4+':
            stories = stories.filter(rating__gte=4)
        elif rating_filter == '3+':
            stories = stories.filter(rating__gte=3)
    
    # Date filtering
    if date_filter:
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if date_filter == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            stories = stories.filter(created_at__gte=start_date)
        elif date_filter == 'week':
            start_date = now - timedelta(days=7)
            stories = stories.filter(created_at__gte=start_date)
        elif date_filter == 'month':
            start_date = now - timedelta(days=30)
            stories = stories.filter(created_at__gte=start_date)
        elif date_filter == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            stories = stories.filter(created_at__gte=start_date)
    
    # Sorting
    valid_sorts = ['-created_at', 'created_at', 'title', '-title', '-rating', '-word_count']
    if sort_by in valid_sorts:
        if sort_by == '-word_count':
            # Custom sorting by word count (calculated field)
            stories = sorted(stories, key=lambda x: x.word_count, reverse=True)
        else:
            stories = stories.order_by(sort_by)
    
    context = {
        'stories': stories,
        'genre_choices': Story.GENRE_CHOICES,
        'length_choices': Story.LENGTH_CHOICES,
        'tone_choices': Story.TONE_CHOICES,
        'current_genre': genre_filter,
        'current_length': length_filter,
        'current_tone': tone_filter,
        'favorites_only': favorites_only,
        'search_query': search_query,
        'current_sort': sort_by,
        'ai_filter': ai_filter,
        'rating_filter': rating_filter,
        'date_filter': date_filter,
    }
    return render(request, 'stories/my_stories.html', context)

@login_required
def story_detail(request, story_id):
    """Detailed view of a single story"""
    story = get_object_or_404(Story, id=story_id, user=request.user)
    return render(request, 'stories/story_detail.html', {'story': story})

def public_gallery(request):
    """Public gallery of stories"""
    stories = Story.objects.filter(is_public=True).order_by('-created_at')
    
    # Filter by genre
    genre_filter = request.GET.get('genre')
    if genre_filter:
        stories = stories.filter(genre=genre_filter)
    
    context = {
        'stories': stories,
        'genre_choices': Story.GENRE_CHOICES,
        'current_genre': genre_filter,
    }
    return render(request, 'stories/gallery.html', context)

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('stories:home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    """User profile page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('stories:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Update stats
    profile.update_stats()
    
    context = {
        'form': form,
        'profile': profile,
        'recent_stories': Story.objects.filter(user=request.user).order_by('-created_at')[:5],
    }
    return render(request, 'stories/profile.html', context)

@login_required
def collections(request):
    """Manage user's story collections"""
    collections = StoryCollection.objects.filter(user=request.user)
    
    # Get collection statistics
    collection_stats = []
    for collection in collections:
        stats = {
            'collection': collection,
            'story_count': collection.story_count,
            'total_words': collection.total_words,
            'genre_distribution': collection.get_genre_distribution(),
            'recent_stories': collection.stories.order_by('-created_at')[:3]
        }
        collection_stats.append(stats)
    
    # Uncategorized stories count
    uncategorized_count = Story.objects.filter(user=request.user, collection__isnull=True).count()
    
    context = {
        'collection_stats': collection_stats,
        'uncategorized_count': uncategorized_count,
        'total_collections': collections.count(),
    }
    return render(request, 'stories/collections.html', context)

@login_required
def create_collection(request):
    """Create a new story collection"""
    if request.method == 'POST':
        form = StoryCollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.save()
            messages.success(request, f'Collection "{collection.name}" created successfully!')
            return redirect('stories:collections')
    else:
        form = StoryCollectionForm()
    
    context = {'form': form, 'title': 'Create New Collection'}
    return render(request, 'stories/collection_form.html', context)

@login_required
def edit_collection(request, collection_id):
    """Edit an existing collection"""
    collection = get_object_or_404(StoryCollection, id=collection_id, user=request.user)
    
    if request.method == 'POST':
        form = StoryCollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, f'Collection "{collection.name}" updated successfully!')
            return redirect('stories:collections')
    else:
        form = StoryCollectionForm(instance=collection)
    
    context = {
        'form': form, 
        'collection': collection,
        'title': f'Edit "{collection.name}"'
    }
    return render(request, 'stories/collection_form.html', context)

@login_required
def delete_collection(request, collection_id):
    """Delete a collection (stories will become uncategorized)"""
    collection = get_object_or_404(StoryCollection, id=collection_id, user=request.user)
    
    if request.method == 'POST':
        collection_name = collection.name
        story_count = collection.story_count
        collection.delete()
        
        messages.success(
            request, 
            f'Collection "{collection_name}" deleted. {story_count} stories moved to uncategorized.'
        )
        return redirect('stories:collections')
    
    context = {'collection': collection}
    return render(request, 'stories/collection_confirm_delete.html', context)

@login_required
def collection_detail(request, collection_id):
    """View stories in a specific collection"""
    collection = get_object_or_404(StoryCollection, id=collection_id, user=request.user)
    stories = collection.stories.order_by('-created_at')
    
    # Apply the same filtering logic as my_stories
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        stories = stories.filter(
            Q(title__icontains=search_query) |
            Q(keywords__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filters
    genre_filter = request.GET.get('genre')
    favorites_only = request.GET.get('favorites')
    sort_by = request.GET.get('sort', '-created_at')
    
    if genre_filter:
        stories = stories.filter(genre=genre_filter)
    if favorites_only:
        stories = stories.filter(is_favorite=True)
    
    # Sorting
    valid_sorts = ['-created_at', 'created_at', 'title', '-title', '-rating']
    if sort_by in valid_sorts:
        stories = stories.order_by(sort_by)
    
    context = {
        'collection': collection,
        'stories': stories,
        'genre_choices': Story.GENRE_CHOICES,
        'search_query': search_query,
        'current_genre': genre_filter,
        'favorites_only': favorites_only,
        'current_sort': sort_by,
    }
    return render(request, 'stories/collection_detail.html', context)

@login_required
def move_to_collection(request):
    """AJAX endpoint to move stories to a collection"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        story_ids = data.get('story_ids', [])
        collection_id = data.get('collection_id')
        
        # Validate collection ownership
        collection = None
        if collection_id:
            try:
                collection = StoryCollection.objects.get(id=collection_id, user=request.user)
            except StoryCollection.DoesNotExist:
                return JsonResponse({'error': 'Collection not found'}, status=404)
        
        # Update stories
        updated_count = Story.objects.filter(
            id__in=story_ids, 
            user=request.user
        ).update(collection=collection)
        
        collection_name = collection.name if collection else "Uncategorized"
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} stories moved to "{collection_name}"',
            'updated_count': updated_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
