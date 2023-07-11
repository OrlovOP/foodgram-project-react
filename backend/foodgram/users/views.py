from djoser.views import UserViewSet
from rest_framework import status, decorators, permissions, response
from django.shortcuts import get_object_or_404

from users.models import User, Follow
from users.serializers import UsersSerializer
from api.serializers import FollowSerializer
from api.pagination import LimitPageNumberPagination


# fmt: off
class MyUserViewSet(UserViewSet):
    '''Вьюсет  модели пользователя.'''

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = LimitPageNumberPagination

    @decorators.action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        '''Подписка или отписка на пользователя.'''

        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            serializer = FollowSerializer(author, data=request.data,
                                          context={'request': request})
            serializer.is_valid()
            Follow.objects.create(user=user, author=author)
            return response.Response(serializer.data,
                                     status=status.HTTP_201_CREATED)
        get_object_or_404(Follow, user=user, author=author).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        '''Возвращаем список авторов, на которых
           подписан текущий пользователь.'''

        return self.get_paginated_response(
            FollowSerializer(
                self.paginate_queryset(
                    User.objects.filter(following__user=request.user)
                ),
                many=True,
                context={'request': request},
            ).data
        )
