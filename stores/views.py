from django.shortcuts import render

# StoreView , an APIView view to return all stores by a particular user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Store
from .serializers import StoreSerializer, StoreGetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class StoreView(APIView):
    """
    API view to return all stores by a particular user"""

    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        stores = Store.objects.filter(owner=user)
        serializer = StoreGetSerializer(stores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        data["owner"] = request.user.id
        serializer = StoreSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreDetailView(APIView):
    """API view to return a single store by a particular user, edit store and delete store"""

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        store_id = id
        store = Store.objects.get(id=store_id)
        serializer = StoreGetSerializer(store)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        store_id = id
        store = Store.objects.get(id=store_id)
        data = request.data
        serializer = StoreSerializer(store, data=data, partial=True)
        if serializer.is_valid():
            store = serializer.save()
            return Response(StoreGetSerializer(store).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(seelf, request, id):
        store_id = id
        store = Store.objects.get(id=store_id)
        store.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
