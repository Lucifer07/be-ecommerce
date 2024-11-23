import mimetypes
import requests
from rest_framework.views import APIView
from rest_framework import status
from django.core.files.base import ContentFile
from io import BytesIO
from .models import Product
from .serializers import ProductSerializer, ProductUpdateSerializer
from .utils import sync_airtable_to_products, put_products_to_airtable, delete_products_from_airtable
from ecommerce.permissions import  IsAdminRole
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from ecommerce.Response.response import Response
class ProductListPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100 
class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        paginator = ProductListPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    def post(self, request):
        permission_classes = [IsAuthenticated, IsAdminRole]
        for permission in permission_classes:
            if not permission().has_permission(request, self):
                return Response(message="Unauthorized", error="UNAUTHORIZED", status=403).Send()
        data = sync_airtable_to_products()
        for item in data:
            fields = item['fields']
            atId = fields['id']
            image_url = fields.get('image', [{}])[0].get('url') if fields.get('image') else None
            defaults = {
                'atId': atId,
                "name": fields['name'],
                'description': fields['description'],
                'price': fields['price'],
                'stock': fields['stock'],
                'created_at': fields['created_at'],
                'updated_at': fields['updated_at'],
            }
            response = requests.get(image_url)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type')
                ext = mimetypes.guess_extension(content_type) or '.jpg'
                image_name = f"{fields['name'].replace(' ', '_').lower()}{ext}"
                image_content = ContentFile(BytesIO(response.content).read(), name=image_name)
                defaults['image'] = image_content
            Product.objects.update_or_create(
                atId=atId,
                defaults=defaults
            )
        return Response(message="Products synced successfully", status=201).Send()


class ProductDetailView(APIView):

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(data=serializer.data, status=status.HTTP_200_OK).Send()
        except Product.DoesNotExist:
            return Response(message="Product not found", error="NOT_FOUND", status=200).Send()

    def put(self, request, pk):
        permission_classes = [IsAuthenticated, IsAdminRole]
        for permission in permission_classes:
            if not permission().has_permission(request, self):
                return Response(message="Unauthorized", error="UNAUTHORIZED", status=403).Send()
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductUpdateSerializer(product, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                put_products_to_airtable(product.atId,serializer.data)
                return Response(data=serializer.data, message="Product updated successfully", status=200).Send()
            return Response(message=serializer.errors, error="INVALID_DATA", status=400).Send()
        except Product.DoesNotExist:
            return Response(message="Product not found", error="NOT_FOUND", status=200).Send()

    def delete(self, request, pk):
        permission_classes = [IsAuthenticated, IsAdminRole]
        for permission in permission_classes:
            if not permission().has_permission(request, self):
                return Response(message="Unauthorized", error="UNAUTHORIZED", status=403).Send()
        try:
            product = Product.objects.get(pk=pk)
            delete_products_from_airtable(product)
            product.delete()
            return Response(message="Product deleted successfully", status=204).Send()
        except Product.DoesNotExist:
            return Response(message="Product not found", error="NOT_FOUND", status=200).Send()
