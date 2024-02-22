from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user01 = User.objects.create_user(username='linfo-kr', password='linfo-kr')
        self.user02 = User.objects.create_user(username='linfo-us', password='linfo-us')
        
    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)
        
        logoBtn = navbar.find('a', text = 'Linfo-KR')
        self.assertEqual(logoBtn.attrs['href'], '/')
        
        homeBtn = navbar.find('a', text = 'Home')
        self.assertEqual(homeBtn.attrs['href'], '/')
        
        blogBtn = navbar.find('a', text = 'Blog')
        self.assertEqual(blogBtn.attrs['href'], '/blog/')
        
        aboutMeBtn = navbar.find('a', text = 'About Me')
        self.assertEqual(aboutMeBtn.attrs['href'], '/about_me/')
        
    def test_post_list(self):
        # 1.1 Get PostList Page
        response = self.client.get('/blog/')
        # 1.2 Succesfully Loaded Page
        self.assertEqual(response.status_code, 200)
        # 1.3 Page Title is 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        # 1.4 Navigation Bar Test
        self.navbar_test(soup)
        
        # 2.1 If there are no Posts in MainArea?
        self.assertEqual(Post.objects.count(), 0)
        # 2.2 View 'Any Posts not Exist'
        mainArea = soup.find('div', id='main-area')
        self.assertIn('Any Posts not Exist', mainArea.text)
        
        # 3.1 If Posts are two?
        post001 = Post.objects.create(
            title = 'First Post',
            content = 'This is First Post',
            author = self.user01
        )
        post002 = Post.objects.create(
            title = 'Second Post',
            content = 'This is Second Post',
            author = self.user02
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
        # 3.5 Username Check
        self.assertIn(self.user01.username.upper(), mainArea.text)
        self.assertIn(self.user02.username.upper(), mainArea.text)
        
    def test_post_detail(self):
        # 1.1 One Post is Exist
        post001 = Post.objects.create(
            title = 'First Post',
            content = 'This is First Post',
            author = self.user01,
        )
        # 1.2 The Post's URL is '/blog/1/'
        self.assertEqual(post001.get_absolute_url(), '/blog/1/')
        
        # 2.0 Detail Page Test of First Post
        # 2.1 Approaching url on the first post works fine(status code: 200)
        response = self.client.get(post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 Navigation Bar Test
        self.navbar_test(soup)
        # 2.3 The title of the first post is in the Web browser tab title
        self.assertIn(post001.title, soup.title.text)
        # 2.4 The title of the first post exists in the post area
        mainArea = soup.find('div', id="main-area")
        postArea = soup.find('div', id="post-area")
        self.assertIn(post001.title, postArea.text)
        # 2.5 The author of the first post exists in the post area(None Development)
        self.assertIn(self.user01.username.upper(), postArea.text)
        # 2.6 The content of the first post exists in the post area
        self.assertIn(post001.content, postArea.text)