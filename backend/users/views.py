from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from users.serializers import FollowSerializer, CustomUserSerializer
from users.models import Follow
from api.pagination import CustomPagination

User = get_user_model()

   
class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей и подписок на них."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        serializer_class=FollowSerializer
    )
    def subscriptions(self, request):
        user = request.user
        favorites = user.follower.all()
        users_id = [favorite_instance.following.id for favorite_instance in favorites]
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
        following = get_object_or_404(User, pk=id)
        
        if request.method == 'POST':
            Follow.objects.create(user=user, following=following)
            serializer = self.get_serializer(following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Follow.objects.filter(user=user, following=following).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
