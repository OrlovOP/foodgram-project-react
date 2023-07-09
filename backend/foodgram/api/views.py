from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.shortcuts import get_object_or_404, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status, decorators, permissions, response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import AuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter
from .pagination import LimitPageNumberPagination
from .utils import create_model_instance, delete_model_instance

from api.serializers import (UsersSerializer,
                             FavoriteSerializer, FollowSerializer,
                             RecipeGetSerializer, RecipePostSerializer,
                             TagSerializer, IngredientSerializer,
                             CartSerializer
                             )
from users.models import User, Follow
from recipes.models import (Recipe, Favorite, Cart, RecipeIngredient,
                            Ingredient, Tag)

# --------------- Приложение users --------------------


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


# -------------- Приложение API ----------------------


class IngredientViewSet(ModelViewSet):
    '''Вьюсет списка ингредиентов.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    '''Вьюсет тэгов.'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    '''Управление рецептами: Создание/изменение/удаление рецепта.
       Добавление рецептов в избранное и список покупок.
       Выгрузка списка покупок.'''

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer


    @decorators.action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        '''Добавление или удаление рецептов в избранном.'''

        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)

        if request.method == 'DELETE':
            error_message = 'Даного рецепта нет в избранном.'
            return delete_model_instance(request, Favorite,
                                         recipe, error_message)

    @decorators.action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        '''Добавление или удаление записей в списке покупок.'''

        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe,
                                         CartSerializer)

        if request.method == 'DELETE':
            error_message = 'Данного рецепта нет в списке покупок.'
            return delete_model_instance(request, Cart,
                                         recipe, error_message)

    @decorators.action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        '''Функция выгрузки списка покупок.'''

        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Мой список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
