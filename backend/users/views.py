from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from api.pagination import LimitPageNumberPagination
from users.serializers import FollowSerializer, CustomUserSerializer
from users.models import Follow

User = get_user_model()


# class CustomUserViewSet(UserViewSet):
#     # pagination_class = LimitPageNumberPagination

#     @action(detail=True, permission_classes=[IsAuthenticated])
#     def subscribe(self, request, id=None):
#         user = request.user
#         following = get_object_or_404(User, id=id)

#         # if user == author:
#         #     return Response({
#         #         'errors': 'Вы не можете подписываться на самого себя'
#         #     }, status=status.HTTP_400_BAD_REQUEST)
#         # if Follow.objects.filter(user=user, author=author).exists():
#         #     return Response({
#         #         'errors': 'Вы уже подписаны на данного пользователя'
#         #     }, status=status.HTTP_400_BAD_REQUEST)

#         follow = Follow.objects.create(user=user, following=following)
#         serializer = FollowSerializer(
#             follow, context={'request': request}
#         )
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     @subscribe.mapping.delete
#     def del_subscribe(self, request, id=None):
#         user = request.user
#         following = get_object_or_404(User, id=id)
#         # if user == author:
#         #     return Response({
#         #         'errors': 'Вы не можете отписываться от самого себя'
#         #     }, status=status.HTTP_400_BAD_REQUEST)
#         follow = Follow.objects.filter(user=user, following=following)
#         if follow.exists():
#             follow.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)

#         return Response({
#             'errors': 'Вы уже отписались'
#         }, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=False, permission_classes=[IsAuthenticated])
#     def subscriptions(self, request):
#         user = request.user
#         queryset = Follow.objects.filter(user=user)
#         pages = self.paginate_queryset(queryset)
#         serializer = FollowSerializer(
#             pages,
#             many=True,
#             context={'request': request}
#         )
#         return self.get_paginated_response(serializer.data)

   
class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей и подписок на них."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        serializer_class=FollowSerializer
    )
    def subscriptions(self, request):
        user = request.user
        favorites = user.followers.all()
        users_id = [favorite_instance.author.id for favorite_instance in favorites]
        users = User.objects.filter(id__in=users_id)
        paginated_queryset = self.paginate_queryset(users)
        serializer = self.serializer_class(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        
        if request.method == 'POST':
            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)