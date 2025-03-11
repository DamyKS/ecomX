from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from stores.models import Store


from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from stores.models import Store
from .serializers import ProductSerializer


class CategoryAPIView(APIView):
    """
    Handles:
      - GET /api/categories/?store={store_id}
      - POST /api/categories/
    """

    def get(self, request):
        print("get called")
        try:
            print("Getting categories")
            store_id = request.query_params.get("store")
            store = Store.objects.get(id=store_id)
            categories = store.categories.all()  # Use .all() to get the queryset
            print(len(categories), "categories found")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Category added successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ProductAPIView(APIView):
#     """
#     Handles:
#       - GET /api/products/?store={store_id}
#       - POST /api/products/
#     """

#     def get(self, request):
#         try:
#             store_id = request.query_params.get("store")
#             store = Store.objects.get(id=store_id)
#             products = store.products.all()
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

#         serializer = ProductSerializer(products, many=True)
#         # Returns full details as per the serializer.
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message": "Product added successfully!"},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ProductDetailAPIView(APIView):
#     """
#     Handles:
#         - GET /api/products/{product_id}/
#       - PUT /api/products/{product_id}/
#       - DELETE /api/products/{product_id}/
#     """

#     def get_object(self, product_id):
#         try:
#             return Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return None

#     def get(self, request, product_id):
#         try:
#             product = Product.objects.get(id=product_id)
#             serializer = ProductSerializer(product)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Product.DoesNotExist:
#             return Response(
#                 {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
#             )

#     def put(self, request, product_id):
#         product = self.get_object(product_id)
#         if not product:
#             return Response(
#                 {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
#             )
#         # partial=True to allow updating one or more fields.
#         serializer = ProductSerializer(product, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message": "Product updated successfully!"}, status=status.HTTP_200_OK
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, product_id):
#         product = self.get_object(product_id)
#         if not product:
#             return Response(
#                 {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
#             )
#         product.delete()
#         return Response(
#             {"message": "Product deleted successfully!"}, status=status.HTTP_200_OK
#         )


class ProductAPIView(APIView):
    """
    Handles:
      - GET /api/products/?store={store_id}
      - POST /api/products/ (supports multiple images)
    """

    parser_classes = (MultiPartParser, FormParser)  # Support file uploads

    def get(self, request):
        try:
            store_id = request.query_params.get("store")
            store = Store.objects.get(id=store_id)
            products = store.products.all()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product added successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    """
    Handles:
        - GET /api/products/{product_id}/
        - PUT /api/products/{product_id}/ (supports updating images)
        - DELETE /api/products/{product_id}/
    """

    parser_classes = (MultiPartParser, FormParser)  # Support file uploads

    def get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get(self, request, product_id):
        product = self.get_object(product_id)
        if not product:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, product_id):
        product = self.get_object(product_id)
        if not product:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(
            product, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        product = self.get_object(product_id)
        if not product:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        product.delete()
        return Response(
            {"message": "Product deleted successfully!"}, status=status.HTTP_200_OK
        )
