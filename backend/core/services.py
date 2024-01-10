from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response

from api.serializers import RecipeShortSerializer, SubscriptionSerializer
from recipes.models import Recipe, IngredientInRecipe
from users.models import Subscription

User = get_user_model()


def get_author(author_id):
    return get_object_or_404(User, id=author_id)


def make_subscribe(
        request, user, author_id
):
    author = get_author(author_id)
    serializer = SubscriptionSerializer(
        author,
        data=request.data,
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    Subscription.objects.create(user=user, author=author)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def unsubscribe(user, author_id):
    subscription = get_object_or_404(
        Subscription,
        user=user,
        author=get_author(author_id),
    )
    subscription.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def get_author_in_subscription(user):
    return User.objects.filter(author_in_subscription__user=user)


def get_subscription_serializer(request, pages):
    return SubscriptionSerializer(
        pages,
        many=True,
        context=({"request": request})
    )


def add_recipe_to_favorite_or_cart(model, user, id):
    recipe = get_object_or_404(Recipe, id=id)
    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            {"errors": "Вы уже добавили этот рецепт!"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    model.objects.create(user=user, recipe=recipe)
    serializer = RecipeShortSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_recipe_from_favorite_or_cart(model, user, id):
    recipe_in_favorite_or_cart = model.objects.filter(
        user=user, recipe__id=id
    )
    if recipe_in_favorite_or_cart.exists():
        recipe_in_favorite_or_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {"errors": "Вы уже удалили этот рецепт!"},
        status=status.HTTP_400_BAD_REQUEST,
    )


def cart_text(self, user, ingredients, date):
    text = (
        f'Здравствуйте, {user.first_name}!\n\n'
        'Вот ваш список покупок на сегодня.\n\n'
        'Нужно купить:\n\n'
    )
    text += '\n'.join([
        f' - {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]})'
        f' - {ingredient["in_shopping_cart_ingredient_amount"]}'
        for ingredient in ingredients
    ])
    text += '\n\nFoodgram.'
    return text


def create_and_download_shopping_cart(user):
    ingredients = IngredientInRecipe.objects.filter(
        recipe__shopping_cart__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        in_shopping_cart_ingredient_amount=Sum('amount')
    ).order_by('ingredient__name')
    shopping_list_date = timezone.now()
    html = cart_text(
        user, ingredients, shopping_list_date
    )
    pdf_file = BytesIO(html)
    return FileResponse(
        pdf_file,
        as_attachment=True,
        filename='shopping_list.pdf'
    )
