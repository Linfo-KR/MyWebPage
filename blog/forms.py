from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('post', 'author', 'creationTime', 'modificationTime', )