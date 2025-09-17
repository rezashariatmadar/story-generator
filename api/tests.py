from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
import json

from stories.models import Story, StoryCollection
from users.models import UserProfile


class APIAuthenticationTest(APITestCase):
    """Test API authentication and permissions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_unauthenticated_story_generation(self):
        """Test that story generation requires authentication"""
        data = {
            'keywords': 'test',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
        }
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_story_generation(self):
        """Test story generation with proper authentication"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'keywords': 'dragon, magic castle',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'exciting'
        }
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response structure
        response_data = response.json()
        required_fields = [
            'id', 'keywords', 'genre', 'length', 'tone', 'content',
            'created_at', 'generation_method', 'ai_powered'
        ]
        for field in required_fields:
            self.assertIn(field, response_data)


class StoryAPITest(APITestCase):
    """Test Story API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.public_story = Story.objects.create(
            user=self.user,
            keywords='public test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Public story content',
            is_public=True
        )
        
        self.private_story = Story.objects.create(
            user=self.user,
            keywords='private test',
            genre='sci_fi',
            length='medium',
            tone='mysterious',
            content='Private story content',
            is_public=False
        )
        
        self.client = APIClient()
    
    def test_story_list_endpoint(self):
        """Test story list endpoint returns public stories"""
        response = self.client.get('/api/stories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('results', data)
        
        # Should contain public story
        story_ids = [story['id'] for story in data['results']]
        self.assertIn(self.public_story.id, story_ids)
        # Should not contain private story
        self.assertNotIn(self.private_story.id, story_ids)
    
    def test_story_detail_endpoint_public(self):
        """Test accessing public story detail"""
        response = self.client.get(f'/api/stories/{self.public_story.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['id'], self.public_story.id)
        self.assertEqual(data['content'], self.public_story.content)
    
    def test_story_detail_endpoint_private_unauthorized(self):
        """Test accessing private story without authentication"""
        response = self.client.get(f'/api/stories/{self.private_story.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_story_detail_endpoint_private_owner(self):
        """Test accessing private story as owner"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/stories/{self.private_story.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['id'], self.private_story.id)
    
    def test_story_generation_validation(self):
        """Test story generation with invalid data"""
        self.client.force_authenticate(user=self.user)
        
        # Missing required field
        data = {
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
            # Missing 'keywords'
        }
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = response.json()
        self.assertIn('keywords', response_data)
    
    def test_story_generation_with_collection(self):
        """Test story generation with collection assignment"""
        self.client.force_authenticate(user=self.user)
        
        # Create a collection
        collection = StoryCollection.objects.create(
            user=self.user,
            name='Test Collection'
        )
        
        data = {
            'keywords': 'test with collection',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy',
            'collection': collection.id
        }
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify story was assigned to collection
        story_id = response.json()['id']
        story = Story.objects.get(id=story_id)
        self.assertEqual(story.collection, collection)


class ExportAPITest(APITestCase):
    """Test export API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.story = Story.objects.create(
            user=self.user,
            keywords='export test',
            genre='fantasy',
            length='short',
            tone='happy',
            content='This is a test story for export functionality.'
        )
        self.client = APIClient()
    
    def test_export_story_txt_authenticated(self):
        """Test TXT export for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/stories/{self.story.id}/export/txt/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_export_story_html_authenticated(self):
        """Test HTML export for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/stories/{self.story.id}/export/html/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_export_story_pdf_authenticated(self):
        """Test PDF export for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/stories/{self.story.id}/export/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_export_story_unauthorized(self):
        """Test export without authentication"""
        response = self.client.get(f'/api/stories/{self.story.id}/export/txt/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_export_story_wrong_user(self):
        """Test export by different user"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        response = self.client.get(f'/api/stories/{self.story.id}/export/txt/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_export_invalid_format(self):
        """Test export with invalid format"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/stories/{self.story.id}/export/invalid/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_export_multiple_stories(self):
        """Test bulk export of multiple stories"""
        self.client.force_authenticate(user=self.user)
        
        # Create additional stories
        story2 = Story.objects.create(
            user=self.user,
            keywords='second story',
            genre='sci_fi',
            length='medium',
            tone='mysterious',
            content='Second test story for bulk export.'
        )
        
        data = {
            'story_ids': [self.story.id, story2.id],
            'format': 'txt'
        }
        response = self.client.post('/api/export/multiple/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/zip')


class AIStatusAPITest(APITestCase):
    """Test AI status API endpoint"""
    
    def test_ai_status_endpoint(self):
        """Test AI status endpoint response"""
        response = self.client.get('/api/ai-status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        required_fields = ['ai_available', 'model', 'status']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Puter AI should always be available
        self.assertTrue(data['ai_available'])
        self.assertEqual(data['model'], 'claude-sonnet-4')
        self.assertEqual(data['status'], 'ready')


class APIPerformanceTest(APITestCase):
    """Test API performance and edge cases"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_story_generation_with_long_keywords(self):
        """Test story generation with very long keywords"""
        long_keywords = ', '.join(['keyword' + str(i) for i in range(100)])
        
        data = {
            'keywords': long_keywords,
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
        }
        response = self.client.post('/api/stories/generate/', data)
        # Should still work or return appropriate error
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_story_generation_with_special_characters(self):
        """Test story generation with special characters"""
        data = {
            'keywords': 'dragon, magic, 🐉, café, naïve',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
        }
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_concurrent_story_generation(self):
        """Test multiple story generations in succession"""
        data = {
            'keywords': 'concurrent test',
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
        }
        
        responses = []
        for i in range(3):
            response = self.client.post('/api/stories/generate/', data)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_story_list_pagination(self):
        """Test story list pagination"""
        # Create multiple public stories
        for i in range(25):
            Story.objects.create(
                user=self.user,
                keywords=f'test story {i}',
                genre='fantasy',
                length='short',
                tone='happy',
                content=f'Test story content {i}',
                is_public=True
            )
        
        response = self.client.get('/api/stories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)


class APISecurityTest(APITestCase):
    """Test API security measures"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.user_story = Story.objects.create(
            user=self.user,
            keywords='user story',
            genre='fantasy',
            length='short',
            tone='happy',
            content='User story content'
        )
        
        self.client = APIClient()
    
    def test_cannot_access_other_user_stories(self):
        """Test that users cannot access other users' private stories"""
        self.client.force_authenticate(user=self.other_user)
        
        response = self.client.get(f'/api/stories/{self.user_story.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cannot_export_other_user_stories(self):
        """Test that users cannot export other users' stories"""
        self.client.force_authenticate(user=self.other_user)
        
        response = self.client.get(f'/api/stories/{self.user_story.id}/export/txt/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        self.client.force_authenticate(user=self.user)
        
        malicious_keywords = "'; DROP TABLE stories_story; --"
        data = {
            'keywords': malicious_keywords,
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
        }
        
        response = self.client.post('/api/stories/generate/', data)
        # Should either succeed safely or validate input
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
        
        # Verify table still exists
        story_count = Story.objects.count()
        self.assertGreaterEqual(story_count, 1)
    
    def test_xss_protection_in_keywords(self):
        """Test XSS protection in user input"""
        self.client.force_authenticate(user=self.user)
        
        xss_keywords = '<script>alert("xss")</script>'
        data = {
            'keywords': xss_keywords,
            'genre': 'fantasy',
            'length': 'short',
            'tone': 'happy'
        }
        
        response = self.client.post('/api/stories/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Keywords should be stored safely
        story_id = response.json()['id']
        story = Story.objects.get(id=story_id)
        # The keywords should be stored as-is, but handled safely in templates
        self.assertIn('script', story.keywords)
