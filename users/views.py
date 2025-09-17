from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('users:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/'  # Redirect to home page after login


def login_view(request):
    """Login view using class-based view"""
    return CustomLoginView.as_view()(request)


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')


@login_required
def profile(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Update stats
    profile.update_stats()
    
    context = {
        'profile': profile,
        'user': request.user
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'users/profile_edit.html', context)


def public_profile(request, username):
    """Public profile view for other users"""
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    
    # Get public stories
    from stories.models import Story
    public_stories = Story.objects.filter(user=user, is_public=True).order_by('-created_at')[:10]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'public_stories': public_stories,
        'is_own_profile': request.user == user
    }
    return render(request, 'users/public_profile.html', context)
