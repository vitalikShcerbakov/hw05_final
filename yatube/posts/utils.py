from django.core.paginator import Paginator
from django.conf import settings


def get_paginator(post_list, request):
    paginator = Paginator(post_list, settings.AMOUNT_OF_POSTS_TO_DISPLAY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
    