from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from weasyprint import HTML

from recipes.models import (Cart, FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredientAmount, Tag)
from users.models import Subscription, User

from core.filters import IngredientFilter, RecipeFilter
from core.pagination import CartPagination, CustomPagination
from core.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeShortSerializer,
                          SubscriptionSerializer, TagSerializer,
                          WriteRecipeSerializer)


class CustomUserViewSet(UserViewSet):
    """Наследованный джосер вьюсет"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(methods=['post', 'delete'],
            detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = SubscriptionSerializer(data=request.data,
                                                context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            subscription = get_object_or_404(Subscription,
                                             user=request.user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            author_in_subscription__user=request.user
        )
        serializer = SubscriptionSerializer(subscriptions,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для отображения рецептов
    на главной странице, в корзине и в избранном."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return WriteRecipeSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],)
    def favorite(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            if FavoriteRecipe.objects.filter(
                user=self.request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {"errors": "Вы уже добавили этот рецепт!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            FavoriteRecipe.objects.create(
                user=self.request.user,
                recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            del_favorite = FavoriteRecipe.objects.filter(
                user=self.request.user,
                recipe__id=pk)
            if del_favorite.exists():
                del_favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Вы уже удалили этот рецепт!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk):
        self.queryset = Cart.objects.all().order_by('-id',)
        self.pagination_class = CartPagination
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            if Cart.objects.filter(
                user=self.request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {"errors": "Вы уже добавили этот рецепт!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Cart.objects.create(
                user=self.request.user,
                recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            del_Cart = Cart.objects.filter(
                user=self.request.user,
                recipe__id=pk)
            if del_Cart.exists():
                del_Cart.delete()
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

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        self.queryset = Cart.objects.all().order_by('-id',)
        self.pagination_class = CartPagination
        ingredients = RecipeIngredientAmount.objects.filter(
            recipe__shopping_cart__user=self.request.user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount')).values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit')
        html_template = render_to_string('cart/shop_list.html',
                                         {'ingredients': ingredients})
        html = HTML(string=html_template)
        result = html.write_pdf()
        response = HttpResponse(result, content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=shopping_list.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        return response