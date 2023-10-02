from django.test import TestCase
from app.models import Post, CustomUser as User

class AppTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='testuser', password='12345')
        cls.user2 = User.objects.create_user(username='testuser2', password='12345')

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        response = self.client.get('/create-post')
        self.assertEqual(response.status_code, 302)

    def test_search(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Không tìm thấy kết quả")

    def test_upload_avatar(self):
        response = self.client.get('/api/upload_avatar')
        self.assertEqual(response.status_code, 302)

        # Login
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/api/upload_avatar')
        self.assertEqual(response.status_code, 200)

        # Upload avatar
        with open('static/user_layout/images/default-avatar.jpg', 'rb') as avatar:
            response = self.client.post('/api/upload_avatar', {'avatar': avatar, 'username': 'testuser'})
            self.assertEqual(response.status_code, 200)
            print(response.json())
            self.assertContains(response, "default-avatar.jpg")

        # Upload avatar with wrong username
        with open('static/user_layout/images/default-avatar.jpg', 'rb') as avatar:
            response = self.client.post('/api/upload_avatar', {'avatar': avatar, 'username': 'testuser2'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "error")
    
