from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from users.serializers import FollowSerializer, FollowListSerializer, CustomUserSerializer
from users.models import Follow, User
from api.pagination import CustomPagination

   
class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей и подписок на них."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )

    def subscriptions(self, request):
        followings = User.objects.filter(following__user=self.request.user)
        paginated_followings = self.paginate_queryset(followings)
        serializer = FollowListSerializer(
            paginated_followings,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=[IsAuthenticated],
    )

    def subscribe(self, request, id):
        user = self.request.user
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'user': user.id, 'following': following.id},
                context={'request': request}
            )
            print(serializer)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Follow.objects.filter(user_id=user, following_id=following).delete()
        return Response(
            'Подписка удалена.',
            status=status.HTTP_204_NO_CONTENT
        )
