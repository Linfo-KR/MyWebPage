from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from blog.models import Post


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user01 = User.objects.create_user(username='TestUser01', password='TestUser01')


    def test_landing(self):
        post001 = Post.objects.create(title="First Post", content="First Post for Test", author=self.user01)
        post002 = Post.objects.create(title="Second Post", content="Second Post for Test", author=self.user01)
        post003 = Post.objects.create(title="Third Post", content="Third Post for Test", author=self.user01)
        post004 = Post.objects.create(title="Fourth Post", content="Fourth Post for Test", author=self.user01)
        
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        body = soup.body
        self.assertNotIn(post001.title, body.text)
        self.assertIn(post002.title, body.text)
        self.assertIn(post003.title, body.text)
        self.assertIn(post004.title, body.text)