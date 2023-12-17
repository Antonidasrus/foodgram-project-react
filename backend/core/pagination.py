from rest_framework import pagination

from core.constants import DEFAULT_LIMIT, MAX_LIMIT, MAX_PAGE_SIZE, PAGE_SIZE


class CustomPagination(pagination.PageNumberPagination):
    page_size = PAGE_SIZE
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE


class CartPagination(pagination.LimitOffsetPagination):
    default_limit = DEFAULT_LIMIT
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_limit = MAX_LIMIT
