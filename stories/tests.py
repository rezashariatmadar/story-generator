from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import json

from .models import Story, StoryCollection
from .puter_ai_service import puter_ai_generator
from .forms import StoryGenerationForm, StoryCollectionForm
from users.models import UserProfile


class StoryModelTest(TestCase):
    """Test the Story model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.collection = StoryCollection.objects.create(
            user=self.user,
            name='Test Collection',
            description='Test description'
        )
    
    def test_story_creation(self):
        """Test creating a story"""
        story = Story.objects.create(
            user=self.user,
            keywords='dragon, magic',
            genre='fantasy',
            length='short',
            tone='exciting',
            content='Once upon a time...',
            collection=self.collection
        )
        
        self.assertEqual(story.user, self.user)
        self.assertEqual(story.keywords, 'dragon, magic')
        self.assertEqual(story.genre, 'fantasy')
        self.assertFalse(story.is_favorite)
        self.assertFalse(story.is_public)
        self.assertEqual(story.rating, 0)
        self.assertTrue(story.created_at)
        
    def test_story_str_method(self):
        """Test story string representation"""
        story = Story.objects.create(
            user=self.user,
            keywords='test keywords',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Test content'
        )
        expected = f"Story by {self.user.username} - test keywords"
        self.assertEqual(str(story), expected)
    
    def test_story_word_count(self):
        """Test word count calculation"""
        story = Story.objects.create(
            user=self.user,
            keywords='test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='This is a test story with ten words exactly here.'
        )
        self.assertEqual(story.word_count, 10)
    
    def test_story_get_absolute_url(self):
        """Test story absolute URL"""
        story = Story.objects.create(
            user=self.user,
            keywords='test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Test content'
        )
        expected_url = f'/stories/{story.id}/'
        self.assertEqual(story.get_absolute_url(), expected_url)


class StoryCollectionModelTest(TestCase):
    """Test the StoryCollection model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_collection_creation(self):
        """Test creating a collection"""
        collection = StoryCollection.objects.create(
            user=self.user,
            name='My Collection',
            description='Test description',
            color='#ff0000',
            icon='fas fa-book'
        )
        
        self.assertEqual(collection.user, self.user)
        self.assertEqual(collection.name, 'My Collection')
        self.assertEqual(collection.color, '#ff0000')
        self.assertFalse(collection.is_default)
    
    def test_collection_str_method(self):
        """Test collection string representation"""
        collection = StoryCollection.objects.create(
            user=self.user,
            name='Test Collection'
        )
        expected = f"{self.user.username} - Test Collection"
        self.assertEqual(str(collection), expected)
    
    def test_default_collection_signal(self):
        """Test that default collection is created for new users"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        
        # Check if default collection was created
        default_collection = StoryCollection.objects.filter(
            user=new_user,
            is_default=True
        ).first()
        
        self.assertIsNotNone(default_collection)
        self.assertEqual(default_collection.name, 'My Stories')


class PuterAIServiceTest(TestCase):
    """Test the Puter AI service"""
    
    def test_ai_service_availability(self):
        """Test that AI service reports as available"""
        self.assertTrue(puter_ai_generator.is_available())
    
    def test_story_generation_returns_claude_marker(self):
        """Test that story generation returns Claude marker"""
        result = puter_ai_generator.generate_story(
            'dragon, magic',
            'fantasy',
            'short',
            'exciting'
        )
        
        self.assertEqual(result['generation_method'], 'ai')
        self.assertEqual(result['ai_model_used'], 'claude-sonnet-4')
        self.assertTrue(result['content'].startswith('PUTER_CLAUDE_GENERATION||'))
        self.assertIn('prompt', result)
    
    def test_template_fallback(self):
        """Test template generation fallback"""
        # Test the _generate_simple method directly
        result = puter_ai_generator._generate_simple(
            'test keywords',
            'fantasy',
            'short',
            'happy'
        )
        
        self.assertEqual(result['generation_method'], 'template')
        self.assertEqual(result['ai_model_used'], 'template-based')
        self.assertNotEqual(result['content'], '')
        self.assertIn('test keywords', result['content'] or '')


class StoryFormsTest(TestCase):
    """Test story-related forms"""
    
    def test_story_generation_form_valid(self):
        """Test valid story generation form"""
        form_data = {
            'keywords': 'dragon, magic',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'exciting'
        }
        form = StoryGenerationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_story_generation_form_invalid(self):
        """Test invalid story generation form"""
        form_data = {
            'keywords': '',  # Required field
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'exciting'
        }
        form = StoryGenerationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('keywords', form.errors)
    
    def test_story_collection_form_valid(self):
        """Test valid story collection form"""
        form_data = {
            'name': 'My Collection',
            'description': 'Test description',
            'color': '#ff0000',
            'icon': 'fas fa-book'
        }
        form = StoryCollectionForm(data=form_data)
        self.assertTrue(form.is_valid())


class StoryViewsTest(TestCase):
    """Test story views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.story = Story.objects.create(
            user=self.user,
            keywords='test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Test story content'
        )
    
    def test_story_list_view_anonymous(self):
        """Test story list view for anonymous users"""
        response = self.client.get(reverse('stories:story_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Stories')
    
    def test_story_detail_view(self):
        """Test story detail view"""
        response = self.client.get(
            reverse('stories:story_detail', kwargs={'pk': self.story.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.story.content)
    
    def test_generate_story_view_requires_login(self):
        """Test that generate story view requires login"""
        response = self.client.get(reverse('stories:generate'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_generate_story_view_authenticated(self):
        """Test generate story view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stories:generate'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generate Your Story')
    
    def test_my_stories_view_requires_login(self):
        """Test that my stories view requires login"""
        response = self.client.get(reverse('stories:my_stories'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_my_stories_view_authenticated(self):
        """Test my stories view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stories:my_stories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Stories')


class APIEndpointsTest(APITestCase):
    """Test API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.story = Story.objects.create(
            user=self.user,
            keywords='test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Test story content'
        )
    
    def test_ai_status_endpoint(self):
        """Test AI status endpoint"""
        response = self.client.get('/api/ai-status/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('ai_available', data)
        self.assertIn('model', data)
        self.assertIn('status', data)
        self.assertTrue(data['ai_available'])  # Puter AI should always be available
    
    def test_story_generation_endpoint_requires_auth(self):
        """Test that story generation requires authentication"""
        data = {
            'keywords': 'test',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
        }
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_story_generation_endpoint_authenticated(self):
        """Test story generation with authentication"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'keywords': 'dragon, magic',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'exciting'
        }
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        self.assertIn('content', response_data)
        self.assertIn('generation_method', response_data)
        self.assertIn('ai_powered', response_data)
    
    def test_story_list_api_endpoint(self):
        """Test story list API endpoint"""
        # Make story public for testing
        self.story.is_public = True
        self.story.save()
        
        response = self.client.get('/api/stories/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
    
    def test_story_detail_api_endpoint(self):
        """Test story detail API endpoint"""
        response = self.client.get(f'/api/stories/{self.story.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['id'], self.story.id)
        self.assertEqual(data['keywords'], self.story.keywords)


class TemplateValidationTest(TestCase):
    """Test template files for syntax errors"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.story = Story.objects.create(
            user=self.user,
            keywords='test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Test story content'
        )
    
    def test_base_template_renders(self):
        """Test that base template renders without errors"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Check for common base template elements
        self.assertContains(response, '<html')
        self.assertContains(response, '</html>')
    
    def test_story_generation_template_renders(self):
        """Test story generation template"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stories:generate'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generate Your Story')
        self.assertContains(response, 'puter.ai.chat')  # Check for Puter.js integration
    
    def test_story_list_template_renders(self):
        """Test story list template"""
        response = self.client.get(reverse('stories:story_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stories')
    
    def test_story_detail_template_renders(self):
        """Test story detail template"""
        response = self.client.get(
            reverse('stories:story_detail', kwargs={'pk': self.story.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.story.content)
    
    def test_my_stories_template_renders(self):
        """Test my stories template"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stories:my_stories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Stories')
    
    def test_collections_template_renders(self):
        """Test collections template"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stories:collections'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Collections')


class ExportServiceTest(TestCase):
    """Test export functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.story = Story.objects.create(
            user=self.user,
            keywords='test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Test story content for export testing.'
        )
    
    def test_export_story_txt(self):
        """Test TXT export"""
        from .export_service import export_story_txt
        
        response = export_story_txt(self.story)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_export_story_html(self):
        """Test HTML export"""
        from .export_service import export_story_html
        
        response = export_story_html(self.story)
        self.assertEqual(response['Content-Type'], 'text/html')
        self.assertIn('attachment', response['Content-Disposition'])


class AuthenticationFlowTest(TestCase):
    """Test authentication flows"""
    
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('users:register'), self.user_data)
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Check if UserProfile was created
        user = User.objects.get(username='testuser')
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_user_login(self):
        """Test user login"""
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Test login
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('users:login'), login_data)
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
    
    def test_protected_views_require_login(self):
        """Test that protected views require login"""
        protected_urls = [
            reverse('stories:generate'),
            reverse('stories:my_stories'),
            reverse('stories:collections'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login
