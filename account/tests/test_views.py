from django.test import TestCase
from app.models import CustomUser as User

class AccountViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='testpassword',
            email='test@gmail.com',
            is_active=True)
        cls.user.save()

    def test_login_view(self):
        response = self.client.get('/account/signin/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(
            '/account/signin/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
    
    def test_login_fail(self):
        response = self.client.post(
            '/account/signin/', {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tài khoản không tồn tại hoặc sai tên đăng nhập hoặc sai mật khẩu')

    def test_signup_view(self):
        response = self.client.get('/account/signup/')
        self.assertEqual(response.status_code, 200)

    def test_signup_success(self):
        response = self.client.post('/account/signup/',
                                    {
                                      'first_name': 'test',
                                      'last_name': 'user2',
                                      'username': 'testuser2',
                                      'email': 'abc@gmail.com',
                                      'password1': 'testpassword',
                                      'password2': 'testpassword'})
        self.assertEqual(response.status_code, 302)

    def test_signup_fail_short_password(self):
        response = self.client.post('/account/signup/',
                                    {
                                      'first_name': 'test',
                                      'last_name': 'user2',
                                      'username': 'testuser3',
                                      'email': 'a@gmail.com',
                                      'password1': 'test',
                                      'password2': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mật khẩu quá ngắn')

    def test_signup_fail_password_not_match(self):
        response = self.client.post('/account/signup/',
                                    {
                                      'first_name': 'test',
                                      'last_name': 'user2',
                                      'username': 'testuser4',
                                      'email': 'a@gmail.com',
                                      'password1': 'testpassword',
                                      'password2': 'testpassword2'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hai trường mật khẩu')

    def test_signup_fail_email_exist(self):
        response = self.client.post('/account/signup/',
                                    {
                                      'first_name': 'test',
                                      'last_name': 'user2',
                                      'username': 'testuser5',
                                      'email': 'test@gmail.com',
                                      'password1': 'testpassword',
                                      'password2': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email đã')
        
    def test_signup_fail_username_exist(self):
        response = self.client.post('/account/signup/',
                                    {
                                      'first_name': 'test',
                                      'last_name': 'user2',
                                      'username': 'testuser',
                                      'email': 'agfh@gmail.com',
                                      'password1': 'testpassword',
                                      'password2': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tên đăng nhập đã được sử dụng')                                                     

    def test_reset_password_view(self):
        response = self.client.get('/account/password_reset/')
        self.assertEqual(response.status_code, 200)
      
    def test_logout_view(self):
        # login first
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/account/signout/')
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_view(self):
        # login first
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/account/{}/edit'.format(self.user.username))
        self.assertEqual(response.status_code, 200)

    def test_profile_view(self):
        response = self.client.get('/account/{}'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
