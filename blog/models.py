import os

from django.db import models

class Post(models.Model) :
    title = models.CharField(max_length=30)
    hookText = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    createTime = models.DateTimeField(auto_now_add = True)
    updateTime = models.DateTimeField(auto_now = True)
    headImage = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    fileUpload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)
    # author = None / Preparing...
    
    def __str__(self):
        return f'[{self.pk}]{self.title}'
    
    def get_absolute_url(self):
        return f'/blog/{self.pk}'
    
    def get_file_name(self):
        return os.path.basename(self.fileUpload.name)
    
    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]