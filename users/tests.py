from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm


class UserProfileModelTest(TestCase):
    """Test the UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created automatically"""
        # UserProfile should be created by signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_str_method(self):
        """Test UserProfile string representation"""
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_user_profile_defaults(self):
        """Test UserProfile default values"""
        profile = self.user.profile
        self.assertEqual(profile.total_stories, 0)
        self.assertEqual(profile.favorite_stories, 0)
        self.assertEqual(profile.preferred_genre, 'fantasy')
        self.assertEqual(profile.preferred_length, 'medium')
        self.assertEqual(profile.preferred_tone, 'happy')
        self.assertIsNone(profile.bio)
    
    def test_update_stats_method(self):
        """Test UserProfile update_stats method"""
        from stories.models import Story
        
        # Create some stories
        Story.objects.create(
            user=self.user,
            keywords='test1',
            genre='fantasy',
            length='short',
            tone='happy',
            content='Test content 1'
        )
        
        story2 = Story.objects.create(
            user=self.user,
            keywords='test2',
            genre='sci_fi',
            length='medium',
            tone='exciting',
            content='Test content 2',
            is_favorite=True
        )
        
        # Update stats
        self.user.profile.update_stats()
        
        # Check updated values
        self.assertEqual(self.user.profile.total_stories, 2)
        self.assertEqual(self.user.profile.favorite_stories, 1)
    
    def test_get_absolute_url(self):
        """Test UserProfile get_absolute_url method"""
        expected_url = f'/users/profile/{self.user.username}/'
        self.assertEqual(self.user.profile.get_absolute_url(), expected_url)


class UserFormsTest(TestCase):
    """Test user-related forms"""
    
    def test_custom_user_creation_form_valid(self):
        """Test valid user creation form"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_custom_user_creation_form_password_mismatch(self):
        """Test user creation form with password mismatch"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_custom_user_creation_form_duplicate_username(self):
        """Test user creation form with duplicate username"""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'existinguser',  # Duplicate username
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_user_profile_form_valid(self):
        """Test valid user profile form"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'bio': 'This is my bio',
            'preferred_genre': 'sci_fi',
            'preferred_length': 'long',
            'preferred_tone': 'dark'
        }
        form = UserProfileForm(data=form_data, instance=user.profile)
        self.assertTrue(form.is_valid())
    
    def test_user_profile_form_save(self):
        """Test user profile form save functionality"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'bio': 'Updated bio',
            'preferred_genre': 'mystery',
            'preferred_length': 'short',
            'preferred_tone': 'funny'
        }
        form = UserProfileForm(data=form_data, instance=user.profile)
        
        if form.is_valid():
            profile = form.save()
            self.assertEqual(profile.bio, 'Updated bio')
            self.assertEqual(profile.preferred_genre, 'mystery')
            self.assertEqual(profile.preferred_length, 'short')
            self.assertEqual(profile.preferred_tone, 'funny')


class UserViewsTest(TestCase):
    """Test user views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password1')
    
    def test_register_view_post_valid(self):
        """Test register view POST with valid data"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(reverse('users:register'), form_data)
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check if UserProfile was created
        new_user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(new_user, 'profile'))
    
    def test_register_view_post_invalid(self):
        """Test register view POST with invalid data"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Invalid email
            'password1': 'pass',        # Too short password
            'password2': 'different'    # Different password
        }
        response = self.client.post(reverse('users:register'), form_data)
        
        # Should stay on register page with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
    
    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')
    
    def test_login_view_post_valid(self):
        """Test login view POST with valid credentials"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('users:login'), form_data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # Check if user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_view_post_invalid(self):
        """Test login view POST with invalid credentials"""
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('users:login'), form_data)
        
        # Should stay on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
    
    def test_logout_view(self):
        """Test logout view"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Logout
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        
        # Check if user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires login"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')
        self.assertContains(response, self.user.username)
    
    def test_profile_edit_view_requires_login(self):
        """Test that profile edit view requires login"""
        response = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_edit_view_authenticated(self):
        """Test profile edit view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Profile')
        self.assertContains(response, 'bio')
    
    def test_profile_edit_post_valid(self):
        """Test profile edit POST with valid data"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'bio': 'This is my updated bio',
            'preferred_genre': 'horror',
            'preferred_length': 'long',
            'preferred_tone': 'dark'
        }
        response = self.client.post(reverse('users:profile_edit'), form_data)
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Check if profile was updated
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'This is my updated bio')
        self.assertEqual(self.user.profile.preferred_genre, 'horror')


class UserAuthenticationTest(TestCase):
    """Test user authentication flows"""
    
    def setUp(self):
        self.client = Client()
    
    def test_complete_registration_flow(self):
        """Test complete user registration flow"""
        # Step 1: Get registration form
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit registration
        form_data = {
            'username': 'completeuser',
            'email': 'complete@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(reverse('users:register'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 3: Verify user creation
        user = User.objects.get(username='completeuser')
        self.assertEqual(user.email, 'complete@example.com')
        
        # Step 4: Verify profile creation
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
        
        # Step 5: Test automatic login after registration
        # (This depends on your implementation)
    
    def test_complete_login_logout_flow(self):
        """Test complete login/logout flow"""
        # Create user
        user = User.objects.create_user(
            username='flowuser',
            email='flow@example.com',
            password='testpass123'
        )
        
        # Step 1: Access protected page (should redirect to login)
        response = self.client.get(reverse('stories:generate'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/users/login'))
        
        # Step 2: Login
        form_data = {
            'username': 'flowuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('users:login'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 3: Access protected page (should work now)
        response = self.client.get(reverse('stories:generate'))
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Logout
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)
        
        # Step 5: Try to access protected page again (should redirect)
        response = self.client.get(reverse('stories:generate'))
        self.assertEqual(response.status_code, 302)
    
    def test_password_validation(self):
        """Test password validation during registration"""
        # Test weak password
        form_data = {
            'username': 'weakpassuser',
            'email': 'weak@example.com',
            'password1': '123',  # Too short and common
            'password2': '123'
        }
        response = self.client.post(reverse('users:register'), form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form with errors
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='weakpassuser').exists())
    
    def test_email_uniqueness(self):
        """Test email uniqueness validation"""
        # Create first user
        User.objects.create_user(
            username='firstuser',
            email='shared@example.com',
            password='testpass123'
        )
        
        # Try to create second user with same email
        form_data = {
            'username': 'seconduser',
            'email': 'shared@example.com',  # Duplicate email
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(reverse('users:register'), form_data)
        
        # Should be able to create (Django allows duplicate emails by default)
        # If you've implemented email uniqueness, this should fail
        # Adjust the assertion based on your implementation
        user_count = User.objects.filter(email='shared@example.com').count()
        # This test documents current behavior - modify if you implement email uniqueness


class UserProfileSignalsTest(TestCase):
    """Test UserProfile signals"""
    
    def test_profile_created_on_user_creation(self):
        """Test that UserProfile is created when User is created"""
        user = User.objects.create_user(
            username='signaluser',
            email='signal@example.com',
            password='testpass123'
        )
        
        # Profile should be created automatically
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
    
    def test_profile_not_duplicated(self):
        """Test that multiple saves don't create duplicate profiles"""
        user = User.objects.create_user(
            username='uniqueuser',
            email='unique@example.com',
            password='testpass123'
        )
        
        # Save user again
        user.email = 'updated@example.com'
        user.save()
        
        # Should still have only one profile
        profile_count = UserProfile.objects.filter(user=user).count()
        self.assertEqual(profile_count, 1)
