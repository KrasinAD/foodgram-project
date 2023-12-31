from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация проекта."""
    page_size = 6
    page_size_query_param = 'limit'
