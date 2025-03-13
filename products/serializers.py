from rest_framework import serializers
from .models import Category, Product
from stores.models import Store


class CategorySerializer(serializers.ModelSerializer):
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        source="store",  # Maps to the ForeignKey field
        write_only=True,
    )
    # store = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "store_id", "name")  # "store",

    def get_store(self, obj):
        return obj.store.name


# class ProductSerializer(serializers.ModelSerializer):
#     store_id = serializers.PrimaryKeyRelatedField(
#         queryset=Store.objects.all(), source="store", write_only=True
#     )
#     category = serializers.StringRelatedField(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(),
#         source="category",
#         write_only=True,
#         required=False,
#     )
#     # store = serializers.StringRelatedField(read_only=True)

#     class Meta:
#         model = Product
#         fields = (
#             "id",
#             "store_id",
#             # "store",
#             "sku",
#             "selling_type",
#             "images",
#             "weight",
#             "dimensions",
#             "name",
#             "description",
#             "price",
#             "stock",
#             "category",
#             # "image",
#             "category_id",
#         )


from rest_framework import serializers
from .models import Product, Image
from stores.models import Store


class ProductSerializer(serializers.ModelSerializer):
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), source="store", write_only=True
    )
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        # write_only=True,
        required=False,
    )
    # Accept multiple image files from the request
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    # For reading, we can return image URLs from the related Image objects
    images_urls = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "store_id",
            # "sku",
            "selling_type",
            "images",  # write-only: list of image files for uploads
            "images_urls",  # read-only: list of image URLs
            "weight",
            "dimensions",
            "name",
            "description",
            "price",
            "stock",
            "category",
            "category_id",
        )

    def get_images_urls(self, obj):
        # Returns a list of URLs for each image in the product's images.
        request = self.context.get("request")
        return [
            request.build_absolute_uri(image.image.url) if request else image.image.url
            for image in obj.images.all()
        ]

    def create(self, validated_data):
        # Pop out images file data from validated_data if present.
        images_data = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)
        # Create an Image instance for each uploaded file and associate it with the product.
        for image_file in images_data:
            img_instance = Image.objects.create(image=image_file)
            product.images.add(img_instance)
        return product

    def update(self, instance, validated_data):
        # Pop out images data if provided.
        images_data = validated_data.pop("images", None)

        # Update all other fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images_data is not None:
            # If new images are provided, clear existing images.
            instance.images.clear()
            for image_file in images_data:
                img_instance = Image.objects.create(image=image_file)
                instance.images.add(img_instance)
        return instance
