from pathlib import Path
from django.dispatch import receiver
from django.db.models.signals import post_delete
from rest_framework import response, status
from django.shortcuts import get_object_or_404, HttpResponse
from recipes.models import Recipe, RecipeIngredient, Ingredient


# fmt: off
@receiver(post_delete, sender=Recipe)
def delete_image(sender, instance, *a, **kw):
    '''Удаяем рецепт - удаляем картинку.'''

    image = Path(instance.image.path)
    if image.exists():
        image.unlink()


def shopping_list_print(self, request, ingredients):
    '''Выгружает текстовый файл со списком покупок.'''

    user = self.request.user
    filename = f'{user.username}_shopping_list.txt'
    shopping_list = ('Мой список покупок: \n')
    shopping_list += '\n'.join([
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]})'
        f' - {ingredient["amount"]}'
        for ingredient in ingredients
    ])
    response = HttpResponse(
        shopping_list, content_type='shopping_list.txt; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def create_ingredients(ingredients, recipe):
    '''Функция добавления ингредиентов для создания или
       редктирования рецепта. '''

    ingredient_list = []
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(Ingredient,
                                               id=ingredient.get('id'))
        amount = ingredient.get('amount')
        ingredient_list.append(
            RecipeIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    RecipeIngredient.objects.bulk_create(ingredient_list)


def create_model_instance(request, instance, serializer_name):
    '''Функция для добавления рецептов в избранное или в список покупок.'''

    serializer = serializer_name(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return response.Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(request, model_name, instance, error_message):
    '''Функция удаления рецепта из избранного или из списка покупок.'''

    if not model_name.objects.filter(user=request.user,
                                     recipe=instance).exists():
        return response.Response({'errors': error_message},
                                 status=status.HTTP_400_BAD_REQUEST)
    model_name.objects.filter(user=request.user, recipe=instance).delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)
