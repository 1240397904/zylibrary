from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# Create your views here.
from django.urls import reverse


def page_index(request):
    """首页（直接跳转到登录页）"""
    print(1333)
    return redirect(reverse('admin:login'))


@login_required
def page_return(request):
    """还书页面"""
    context = dict(
        admin.site.each_context(request),
        title='还书1111',
    )

    return render(request, 'library/return.html', context)

