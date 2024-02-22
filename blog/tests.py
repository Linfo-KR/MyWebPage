from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_post_list(self):
        # 1.1 Get PostList Page
        response = self.client.get('/blog/')
        # 1.2 Succesfully Loaded Page
        self.assertEqual(response.status_code, 200)
        # 1.3 Page Title is 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        # 1.4 Navigation Bar is Exist
        navbar = soup.nav
        # 1.5 'Blog', 'About Me' in Navigation Bar
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)
        
        # 2.1 If there are no Posts in MainArea?
        self.assertEqual(Post.objects.count(), 0)
        # 2.2 View 'Any Posts not Exist'
        mainArea = soup.find('div', id='main-area')
        self.assertIn('Any Posts not Exist', mainArea.text)
        
        # 3.1 If Posts are two?
        post001 = Post.objects.create(
            title = 'First Post',
            content = 'This is First Post',
        )
        post002 = Post.objects.create(
            title = 'Second Post',
            content = 'This is Second Post',
        )
        self.assertEqual(Post.objects.count(), 2)
        # 3.2 When you reload the Post List page
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # 3.3 Two post titles exist in the main area
        mainArea = soup.find('div', id='main-area')
        self.assertIn(post001.title, mainArea.text)
        self.assertIn(post002.title, mainArea.text)
        # 3.4 The phrase 'Any Posts not Exist' is no longer visible
        self.assertNotIn('Any Posts not Exist', mainArea.text)