from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from products.models import Product
from .serializers import OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer
import requests 
from django.conf import settings as setting
from ecommerce.Response.response import Response
from ecommerce.permissions import IsUserRole
from rest_framework.permissions import IsAuthenticated
import json
from datetime import datetime
from products.utils import update_stock_to_airtable

MONDAY_API_KEY = setting.MONDAY_API_KEY
MONDAY_BOARD_ID = setting.MONDAY_BOARD_ID

class OrderAPIView(APIView):
    def get(self, request):
        permission_classes = [IsAuthenticated,IsUserRole]
        for permission in permission_classes:
            if not permission().has_permission(request, self):
                return Response(message="Unauthorized", error="UNAUTHORIZED", status=403).Send()
        userId = getattr(request.user, 'id', None)()
        if userId ==0:
            return Response(message="User not found", status=status.HTTP_404_NOT_FOUND, error="NOT_FOUND").Send()
        orders = Order.objects.filter(user_id=userId).select_related('user', 'product').all()
        serializer = OrderSerializer(orders, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK, message="Orders fetched successfully").Send()

    def post(self, request):
        permission_classes = [IsAuthenticated,IsUserRole]
        for permission in permission_classes:
            if not permission().has_permission(request, self):
                return Response(message="Unauthorized", error="UNAUTHORIZED", status=403).Send()
        userId = getattr(request.user, 'id', None)()
        if userId ==0:
            return Response(message="User not found", status=status.HTTP_401_UNAUTHORIZED, error="NOT_FOUND").Send()
        email=getattr(request.user, 'email', None)()
        if email =="":
            return Response(message="User not found", status=status.HTTP_401_UNAUTHORIZED, error="NOT_FOUND").Send()
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user_id'] = userId
            price = Product.objects.get(pk=request.data["product_id"]).price
            totalProduct = Product.objects.get(pk=request.data["product_id"]).stock
            atId=Product.objects.get(pk=request.data["product_id"]).atId
            serializer.validated_data['product_id'] = request.data["product_id"]
            serializer.validated_data['price'] = price
            serializer.validated_data['user_email'] = email
            serializer.validated_data['total'] = price*int(request.data["quantity"])
            ids = str(serializer.save())
            res=self.send_to_monday(ids=ids,data=serializer.validated_data)
            if res.status_code == 200:
                idstore = res.json()["data"]["create_item"]["id"]
                Order.objects.filter(id=ids).update(item_id=idstore)
            Product.objects.filter(id=request.data["product_id"]).update(stock=totalProduct-int(request.data["quantity"]))
            update_stock_to_airtable(atId,totalProduct-int(request.data["quantity"]))
            return Response(status=status.HTTP_201_CREATED, message="Order created successfully").Send()
        return Response(message="Invalid data", status=status.HTTP_400_BAD_REQUEST,error="INVALID_DATA").Send()

    def send_to_monday(self, ids, data):
        url = "https://api.monday.com/v2"
        headers = {
            "Authorization": MONDAY_API_KEY,
            "Content-Type": "application/json",
        }
        column_values = json.dumps({
            "numbers": str(data["price"]),
            "status": "pending",
            "email": {"email": data["user_email"], "text": data["user_email"]},
            "numbers0": str(data["total"]),
            "numbers7": str(data["quantity"]),
            "text8": data["product_id"],
            "text2":str(data["user_id"]),
            "date4": datetime.now().strftime("%Y-%m-%d")
        })
        query = f"""
        mutation {{
            create_item(
                board_id: {MONDAY_BOARD_ID}
                group_id: "topics"
                item_name: "Order #{ids}"
                column_values: {json.dumps(column_values)}
            ) {{
                id
            }}
        }}
        """
        response = requests.post(url, json={"query": query}, headers=headers)
        return response  


class DetailOrderAPIView(APIView):
    def get(self, request, pk):
        permission_classes = [IsAuthenticated,IsUserRole]
        for permission in permission_classes:
            if not permission().has_permission(request, self):
                return Response(message="Unauthorized", error="UNAUTHORIZED", status=403).Send()
        userId = getattr(request.user, 'id', None)()
        if userId ==0:
            return Response(message="User not found", status=status.HTTP_401_UNAUTHORIZED, error="NOT_FOUND").Send()
        try:
            order = Order.objects.filter(user_id=userId).select_related('user', 'product').get(pk=pk)
            serializer = OrderSerializer(order)
            return Response(status=status.HTTP_200_OK, data=serializer.data).Send()
        except Order.DoesNotExist:
            return Response(status=status.HTTP_200_OK, data="", message="Order not found", error="NOT_FOUND").Send()

class PaymentGatewayAPIView(APIView):
    def put(self, request, pk):
        permission_classes = [IsAuthenticated,IsUserRole]
        for permission in permission_classes:
            if not permission().has_permission(request, self):
                return Response(message="Unauthorized", error="UNAUTHORIZED", status=403).Send()
        userId = getattr(request.user, 'id', None)()
        if userId ==0:
            return Response(message="User not found", status=status.HTTP_401_UNAUTHORIZED, error="NOT_FOUND").Send()
        try:
            order = Order.objects.filter(user_id=userId).get(pk=pk)
            serialze=UpdateOrderSerializer(order,data=request.data)
            if serialze.is_valid():
                serialze.validated_data['status'] = request.data["status"]
                serialze.save()
                self.update_monday(order.item_id,request.data["status"])
                if request.data["status"]=="failed":
                    Product.objects.filter(id=order.product_id).update(stock=order.product.stock+order.quantity)
                    update_stock_to_airtable(order.product.atId,order.product.stock+order.quantity)
                return Response(data=serialze.data, status=status.HTTP_200_OK, message="Order updated successfully").Send()
            return Response(message=serialze.errors, status=status.HTTP_400_BAD_REQUEST, error="INVALID_DATA").Send()
        except Order.DoesNotExist:
            return Response(status=status.HTTP_200_OK, data="", message="Order not found", error="NOT_FOUND").Send()
    def update_monday(self,ids, status):
        url = "https://api.monday.com/v2"
        headers = {
            "Authorization": MONDAY_API_KEY,
            "Content-Type": "application/json",
        }
        query = f"""
        mutation {{
          change_simple_column_value (
            board_id: {MONDAY_BOARD_ID},
            item_id: {ids},
            column_id: "status",
            value: "{status}"
          ) {{
            id
          }}
        }}
        """
        print(query)
        response = requests.post(url, json={"query": query}, headers=headers)
        print(response.json())
        
