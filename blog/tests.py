from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user01 = User.objects.create_user(username='linfo-kr', password='linfo-kr')
        self.user02 = User.objects.create_user(username='linfo-us', password='linfo-us')
        self.user02.is_staff = True
        self.user02.save()
        
        self.categoryBackend = Category.objects.create(name='Backend', slug='backend')
        self.categoryDeepLearning = Category.objects.create(name='Deep Learning', slug='deep-learning')
        
        self.tagDjango = Tag.objects.create(name='Django', slug='django')
        self.tagReact = Tag.objects.create(name='React', slug='react')
        self.tagFlutter = Tag.objects.create(name='Flutter', slug='flutter')
        
        self.post001 = Post.objects.create(title = 'First Post', content = 'This is First Post', author = self.user01, category=self.categoryBackend)
        self.post002 = Post.objects.create(title = 'Second Post', content = 'This is Second Post', author = self.user02, category=self.categoryDeepLearning)
        self.post003 = Post.objects.create(title = 'Third Post', content = 'This is Third Post', author = self.user02)
        
        self.post001.tags.add(self.tagDjango)
        self.post003.tags.add(self.tagReact)
        self.post003.tags.add(self.tagFlutter)
        
        self.comment001 = Comment.objects.create(post=self.post001, author=self.user01, content='First Comment.')
        
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
        self.assertIn(self.tagDjango.name, post001Card.text)
        self.assertNotIn(self.tagReact.name, post001Card.text)
        self.assertNotIn(self.tagFlutter.name, post001Card.text)
        
        post002Card = mainArea.find('div', id="post-2")
        self.assertIn(self.post002.title, post002Card.text)
        self.assertIn(self.post002.category.name, post002Card.text)
        self.assertNotIn(self.tagDjango.name, post002Card.text)
        self.assertNotIn(self.tagReact.name, post002Card.text)
        self.assertNotIn(self.tagFlutter.name, post002Card.text)
        
        post003Card = mainArea.find('div', id="post-3")
        self.assertIn('Unclassified', post003Card.text)
        self.assertIn(self.post003.title, post003Card.text)
        self.assertNotIn(self.tagDjango.name, post003Card.text)
        self.assertIn(self.tagReact.name, post003Card.text)
        self.assertIn(self.tagFlutter.name, post003Card.text)
        
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
        self.assertEqual(self.post001.get_absolute_url(), '/blog/1/')
    
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post001.title, soup.title.text)

        mainArea = soup.find('div', id="main-area")
        postArea = soup.find('div', id="post-area")
        self.assertIn(self.post001.title, postArea.text)
        self.assertIn(self.categoryBackend.name, postArea.text)
        self.assertIn(self.user01.username.upper(), postArea.text)
        self.assertIn(self.post001.content, postArea.text)
        
        self.assertIn(self.tagDjango.name, postArea.text)
        self.assertNotIn(self.tagReact.name, postArea.text)
        self.assertNotIn(self.tagFlutter.name, postArea.text)
        
        commentArea = soup.find('div', id="comment-area")
        comment001Area = soup.find('div', id="comment-1")
        self.assertIn(self.comment001.author.username, comment001Area.text)
        self.assertIn(self.comment001.content, comment001Area.text)
        
    def test_category_page(self):
        response = self.client.get(self.categoryBackend.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        self.assertIn(self.categoryBackend.name, soup.h1.text)
        
        mainArea = soup.find('div', id="main-area")
        self.assertIn(self.categoryBackend.name, mainArea.text)
        self.assertIn(self.post001.title, mainArea.text)
        self.assertNotIn(self.post002.title, mainArea.text)
        self.assertNotIn(self.post003.title, mainArea.text)
        
    def test_tag_page(self):
        response = self.client.get(self.tagDjango.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        self.assertIn(self.tagDjango.name, soup.h1.text)
        
        mainArea = soup.find('div', id="main-area")
        self.assertIn(self.tagDjango.name, mainArea.text)
        self.assertIn(self.post001.title, mainArea.text)
        self.assertNotIn(self.post002.title, mainArea.text)
        self.assertNotIn(self.post003.title, mainArea.text)
        
    def test_create_post(self):
        # If Not User Login?
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)
        
        # If Not Staff Login?
        self.client.login(username='linfo-kr', password='linfo-kr')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)
        
        # If Staff Login?
        self.client.login(username='linfo-us', password='linfo-us')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual('Create Post - Blog', soup.title.text)
        mainArea = soup.find('div', id='main-area')
        self.assertIn('Create New Post', mainArea.text)
        
        tag_str_input = mainArea.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        
        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Create Post Form',
                'content': 'Create Post Form using Django.',
                'tags_str': 'New Tag; Tag, Flutter'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        lastPost = Post.objects.last()
        self.assertEqual(lastPost.title, "Create Post Form")
        self.assertEqual(lastPost.author.username, 'linfo-us')
        
        self.assertEqual(lastPost.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='New Tag'))
        self.assertTrue(Tag.objects.get(name='Tag'))
        self.assertEqual(Tag.objects.count(), 5)
        
    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post003.pk}/'
        
        # If Not User Login?
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)
        
        # If Login, If Not Post's Author?
        self.assertNotEqual(self.post003.author, self.user01)
        self.client.login(
            username=self.user01.username,
            password='linfo-kr'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)
        
        # If Login and Post's Author?
        self.client.login(
            username=self.post003.author.username,
            password='linfo-us'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual('Edit Post - Blog', soup.title.text)
        mainArea = soup.find('div', id="main-area")
        self.assertIn('Edit Post', mainArea.text)
        
        tag_str_input = mainArea.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('React; Flutter', tag_str_input.attrs['value'])
        
        response = self.client.post(
            update_post_url,
            {
                'title': 'Update Third Post.',
                'content': 'Update Third Post with Django Python Web Development Framework.',
                'category': self.categoryDeepLearning.pk,
                'tags_str': 'React; Pytorch, MySQL'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        mainArea = soup.find('div', id='main-area')
        self.assertIn('Update Third Post.', mainArea.text)
        self.assertIn('Update Third Post with Django Python Web Development Framework.', mainArea.text)
        self.assertIn(self.categoryDeepLearning.name, mainArea.text)
        self.assertIn('React', mainArea.text)
        self.assertIn('Pytorch', mainArea.text)
        self.assertIn('MySQL', mainArea.text)
        self.assertNotIn('Flutter', mainArea.text)
        
    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post001.comment_set.count(), 1)
        
        # If Not User Login?
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        commentArea = soup.find('div', id="comment-area")
        self.assertIn('Log In and Leave a Comment', commentArea.text)
        self.assertFalse(commentArea.find('form', id="comment-form"))
        
        # If User Login?
        self.client.login(username='linfo-kr', password="linfo-kr")
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        commentArea = soup.find('div', id="comment-area")
        self.assertNotIn('Log In and Leave a Comment', commentArea.text)
        
        commentForm = commentArea.find('form', id="comment-form")
        self.assertTrue(commentForm.find('textarea', id="id_content"))
        
        response = self.client.post(
            self.post001.get_absolute_url() + 'new_comment/',
            {
                'content': "First Comments this Post",
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post001.comment_set.count(), 2)
        
        newComment = Comment.objects.last()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(newComment.post.title, soup.title.text)
        
        commentArea = soup.find('div', id="comment-area")
        newCommentDiv = commentArea.find('div', id=f'comment-{newComment.pk}')
        self.assertIn('linfo-kr', newCommentDiv.text)
        self.assertIn('First Comments this Post', newCommentDiv.text)

    def test_comment_update(self):
        commentByUser02 = Comment.objects.create(
            post = self.post001,
            author = self.user02,
            content = 'Second Comment'
        )
        
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        commentArea = soup.find('div', id="comment-area")
        self.assertFalse(commentArea.find('a', id="comment-1-update-btn"))
        self.assertFalse(commentArea.find('a', id="comment-2-update-btn"))
        
        # If User Login?
        self.client.login(username="linfo-kr", password="linfo-kr")
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        commentArea = soup.find('div', id="comment-area")
        self.assertFalse(commentArea.find('a', id="comment-2-update-btn"))
        comment001UpdateBtn = commentArea.find('a', id="comment-1-update-btn")
        self.assertIn('Edit', comment001UpdateBtn.text)
        self.assertEqual(comment001UpdateBtn.attrs['href'], '/blog/update_comment/1/')
        
        response = self.client.get('/blog/update_comment/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual('Edit Comment - Blog', soup.title.text)
        updateCommentForm = soup.find('form', id="comment-form")
        contentTextarea = updateCommentForm.find('textarea', id="id_content")
        self.assertIn(self.comment001.content, contentTextarea.text)
        
        response = self.client.post(
            f'/blog/update_comment/{self.comment001.pk}/',
            {
                'content': 'Update Comment',
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment001Div = soup.find('div', id="comment-1")
        self.assertIn('Update Comment', comment001Div.text)
        self.assertIn('Updated: ', comment001Div.text)
        
    def test_delete_comment(self):
        commentByUser02 = Comment.objects.create(
            post = self.post001,
            author = self.user02,
            content = 'Second Comment'
        )
        
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post001.comment_set.count(), 2)
        
        # If Not User Login?
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        commentArea = soup.find('div', id="comment-area")
        self.assertFalse(commentArea.find('a', id="comment-1-delete-btn"))
        self.assertFalse(commentArea.find('a', id="comment-2-delete-btn"))
        
        # If User Login?
        self.client.login(username='linfo-us', password='linfo-us')
        response = self.client.get(self.post001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        commentArea = soup.find('div', id="comment-area")
        self.assertFalse(commentArea.find('a', id="comment-1-delete-btn"))
        comment002DeleteModalBtn = commentArea.find('a', id="comment-2-delete-modal-btn")
        self.assertIn('Delete', comment002DeleteModalBtn.text)
        self.assertEqual(comment002DeleteModalBtn.attrs['data-target'], '#deleteCommentModal-2')
        
        deleteCommentModal002 = soup.find('div', id="deleteCommentModal-2")
        self.assertIn('Are you Sure?', deleteCommentModal002.text)
        reallyDeleteBtn002 = deleteCommentModal002.find('a')
        self.assertIn('Delete', reallyDeleteBtn002.text)
        self.assertEqual(reallyDeleteBtn002['href'], '/blog/delete_comment/2/')
        
        response = self.client.get('/blog/delete_comment/2/', follow = True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(self.post001.title, soup.title.text)
        commentArea = soup.find('div', id="comment-area")
        self.assertNotIn(commentByUser02.content, commentArea.text)
        
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post001.comment_set.count(), 1)