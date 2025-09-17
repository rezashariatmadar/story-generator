from django import forms
from .models import Story
from users.models import UserProfile
from .models import StoryCollection

class StoryGenerationForm(forms.Form):
    keywords = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter keywords for your story (e.g., "dragon, castle, magic")',
        }),
        help_text='Enter a few words or phrases to inspire your story'
    )
    
    genre = forms.ChoiceField(
        choices=Story.GENRE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='fantasy'
    )
    
    length = forms.ChoiceField(
        choices=Story.LENGTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='short'
    )
    
    tone = forms.ChoiceField(
        choices=Story.TONE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='happy'
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['favorite_genre', 'preferred_length', 'preferred_tone']
        widgets = {
            'favorite_genre': forms.Select(attrs={'class': 'form-control'}),
            'preferred_length': forms.Select(attrs={'class': 'form-control'}),
            'preferred_tone': forms.Select(attrs={'class': 'form-control'}),
        }

class StoryCollectionForm(forms.ModelForm):
    class Meta:
        model = StoryCollection
        fields = ['name', 'description', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter collection name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description for this collection'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'icon': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('fas fa-folder', '📁 Folder'),
                ('fas fa-star', '⭐ Star'),
                ('fas fa-heart', '❤️ Heart'),
                ('fas fa-bookmark', '🔖 Bookmark'),
                ('fas fa-magic', '✨ Magic'),
                ('fas fa-crown', '👑 Crown'),
                ('fas fa-gem', '💎 Gem'),
                ('fas fa-fire', '🔥 Fire'),
                ('fas fa-leaf', '🍃 Leaf'),
                ('fas fa-moon', '🌙 Moon'),
                ('fas fa-sun', '☀️ Sun'),
                ('fas fa-bolt', '⚡ Lightning'),
            ])
        }

class StoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'collection', 'is_public', 'is_favorite', 'rating']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'collection': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rating': forms.Select(
                choices=[(i, f'{i} star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['collection'].queryset = StoryCollection.objects.filter(user=user)
            self.fields['collection'].empty_label = "No Collection" 