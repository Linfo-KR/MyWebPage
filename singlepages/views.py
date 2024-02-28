from django.shortcuts import render

from blog.models import Post

def landing(request):
    recent_posts = Post.objects.order_by('-pk')[:3]
    return render(
        request,
        'singlepages/landing.html',
        {
            'recent_posts': recent_posts,
        }
    )
    
def about_me(request):
    return render(
        request,
        'singlepages/about_me.html'
    )