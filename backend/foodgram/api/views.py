from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.shortcuts import get_object_or_404, HttpResponse
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import decorators
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import AuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter
from .pagination import LimitPageNumberPagination
from .utils import create_model_instance, delete_model_instance

from api.serializers import (
    FavoriteSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    TagSerializer,
    IngredientSerializer,
    CartSerializer,
)
from recipes.models import (
    Recipe,
    Favorite,
    Cart,
    RecipeIngredient,
    Ingredient,
    Tag,
)


# fmt: off
class IngredientViewSet(ModelViewSet):
    '''Вьюсет списка ингредиентов.'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


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
    pagination_class = LimitPageNumberPagination

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
