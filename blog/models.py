from django.db import models

class Post(models.Model) :
    title = models.CharField(max_length = 30)
    content = models.TextField()
    createTime = models.DateTimeField(auto_now_add = True)
    updateTime = models.DateTimeField(auto_now = True)
    headImage = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    # author = None / Preparing...
    
    def __str__(self):
        return f'[{self.pk}]{self.title}'
    
    def get_absolute_url(self):
        return f'/blog/{self.pk}'