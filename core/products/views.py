from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer

# Create your views here.

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsRegularUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_staff

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_serializer(self, *args, **kwargs):
        if 'instance' in kwargs:
            instance = kwargs['instance']
            kwargs['context'] = self.get_serializer_context()
            serializer = self.serializer_class(instance, **kwargs)
            return serializer
        if 'data' in kwargs:
            kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsRegularUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
