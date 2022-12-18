from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related().all()
    paginator = Paginator(post_list, settings.AMOUNT_OF_POSTS_TO_DISPLAY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, settings.AMOUNT_OF_POSTS_TO_DISPLAY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    all_post_user = user_obj.posts.all()
    paginator = Paginator(all_post_user, settings.AMOUNT_OF_POSTS_TO_DISPLAY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    number_of_subscribers = Follow.objects.filter(author=user_obj).count()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            author=user_obj, user=request.user).exists())
    context = {
        'user_obj': user_obj,
        'all_post_user': all_post_user,
        'page_obj': page_obj,
        'following': following,
        'number_of_subscribers': number_of_subscribers,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    form = CommentForm()
    is_edit = False
    one_post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post_id)
    if one_post.author == request.user:
        is_edit = True
    count_post = Post.objects.select_related('author').filter(
        author=one_post.author).count()
    context = {
        'one_post': one_post,
        'count_post': count_post,
        'is_edit': is_edit,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template_name = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
    return render(request, template_name, {'form': form})


@login_required
def post_edit(request, post_id):
    template_name = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, template_name, {
        'form': form,
        'is_edit': is_edit,
        'post': post,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.AMOUNT_OF_POSTS_TO_DISPLAY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (
        Follow.objects.filter(author=author, user=request.user).exists()
            or request.user == author
    ):
        return redirect('posts:profile', username=username)
    Follow.objects.create(author=author, user=request.user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    record = Follow.objects.filter(author=author).filter(user=request.user)
    record.delete()
    return redirect('posts:follow_index')
