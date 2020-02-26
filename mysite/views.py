from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from blog.models import Blog
from django.urls import reverse
from read_statistics.utils import get_seven_days_read_data
from .forms import LoginFrom, RegForm


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    return render(request, 'home.html', context)


def login(request):
    if request.method == 'POST':
        login_form = LoginFrom(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginFrom()

    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)  # 创建用户
            user.save()

            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)


def search(request):
    search_words = request.GET.get('wd', '').strip()
    #  分词
    condition = None
    for word in search_words.split(' '):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)

    search_blogs = []
    if condition is not None:
        # 搜索
        search_blogs = Blog.objects.filter(condition)

    # 分页
    paginator = Paginator(search_blogs, 5)  # 5
    page_num = request.GET.get('page', 1)  # 得参
    page_of_blogs = paginator.get_page(page_num)

    context = {}
    context['search_words'] = search_words
    context['page_of_blogs'] = page_of_blogs
    context['search_blogs_count'] = search_blogs.count()
    return render(request, 'search.html', context)
