from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user01 = User.objects.create_user(username='linfo-kr', password='linfo-kr')
        self.user02 = User.objects.create_user(username='linfo-us', password='linfo-us')
        self.categoryBackend = Category.objects.create(name='Backend', slug='backend')
        self.categoryDeepLearning = Category.objects.create(name='Deep Learning', slug='deep-learning')
        self.post001 = Post.objects.create(title = 'First Post', content = 'This is First Post', author = self.user01, category=self.categoryBackend)
        self.post002 = Post.objects.create(title = 'Second Post', content = 'This is Second Post', author = self.user02, category=self.categoryDeepLearning)
        self.post003 = Post.objects.create(title = 'Third Post', content = 'This is Third Post', author = self.user02)
        
    def category_card_test(self, soup):
        categoriesCard = soup.find('div', id='categories-card')
        self.assertIn('Categories', categoriesCard.text)
        self.assertIn(f'{self.categoryBackend.name} ({self.categoryBackend.post_set.count()})', categoriesCard.text)
        self.assertIn(f'{self.categoryDeepLearning.name} ({self.categoryDeepLearning.post_set.count()})', categoriesCard.text)
        self.assertIn(f'Unclassified (1)', categoriesCard.text)
        
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
        # If Post Exist :
        self.assertEqual(Post.objects.count(), 3)
        
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        mainArea = soup.find('div', id="main-area")
        self.assertNotIn('Any Posts not Exist', mainArea.text)
        
        post001Card = mainArea.find('div', id="post-1")
        self.assertIn(self.post001.title, post001Card.text)
        self.assertIn(self.post001.category.name, post001Card.text)
        post002Card = mainArea.find('div', id="post-2")
        self.assertIn(self.post002.title, post002Card.text)
        self.assertIn(self.post002.category.name, post002Card.text)
        post003Card = mainArea.find('div', id="post-3")
        self.assertIn('Unclassified', post003Card.text)
        self.assertIn(self.post003.title, post003Card.text)
        
        self.assertIn(self.user01.username.upper(), mainArea.text)
        self.assertIn(self.user02.username.upper(), mainArea.text)
        
        # If Post not Exist :
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        mainArea = soup.find('div', id="main-area")
        self.assertIn('Any Posts not Exist', mainArea.text)
        
    def test_post_detail(self):
        # 1.1 One Post is Exist
        # 1.2 The Post's URL is '/blog/1/'
        self.assertEqual(self.post001.get_absolute_url(), '/blog/1/')
        
        # 2.0 Detail Page Test of First Post
        # 2.1 Approaching url on the first post works fine(status code: 200)
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 Navigation Bar Test
        self.navbar_test(soup)
        # 2.3 The title of the first post is in the Web browser tab title
        self.assertIn(self.post001.title, soup.title.text)
        # 2.4 The title of the first post exists in the post area
        mainArea = soup.find('div', id="main-area")
        postArea = soup.find('div', id="post-area")
        self.assertIn(self.post001.title, postArea.text)
        # 2.5 The author of the first post exists in the post area(None Development)
        self.assertIn(self.user01.username.upper(), postArea.text)
        # 2.6 The content of the first post exists in the post area
        self.assertIn(self.post001.content, postArea.text)