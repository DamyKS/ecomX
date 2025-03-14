from rest_framework import serializers
from .models import Category, Product
from stores.models import Store


class CategorySerializer(serializers.ModelSerializer):
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        source="store",  # Maps to the ForeignKey field
        # write_only=True,
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
        required=False,
    )
    # Accept multiple new image files from the request.
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    # A new field: a list of URLs for existing images to keep.
    existing_images = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    # For reading, return image URLs from related Image objects.
    images_urls = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "store_id",
            "selling_type",
            "images",  # new image files for upload
            "existing_images",  # list of URLs to keep
            "images_urls",  # read-only URLs from associated images
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
        request = self.context.get("request")
        return [
            request.build_absolute_uri(image.image.url) if request else image.image.url
            for image in obj.images.all()
        ]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        # existing_images is not used on create.
        validated_data.pop("existing_images", None)
        product = Product.objects.create(**validated_data)
        for image_file in images_data:
            img_instance = Image.objects.create(image=image_file)
            product.images.add(img_instance)
        return product

    def update(self, instance, validated_data):
        # Pop out new images and the list of existing images to keep.
        images_data = validated_data.pop("images", None)
        existing_images = validated_data.pop("existing_images", None)

        # Update all other fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If existing_images is provided, remove only images not in that list.
        if existing_images is not None:
            # Build a list of URLs that we want to keep.
            request = self.context.get("request")

            def get_image_url(image):
                url = image.image.url
                if request:
                    return request.build_absolute_uri(url)
                return url

            # For each associated image, remove if its URL is not in existing_images.
            for img in list(instance.images.all()):
                if get_image_url(img) not in existing_images:
                    # Remove image from product and optionally delete it.
                    instance.images.remove(img)
                    img.delete()
        # If new images are provided, add them.
        if images_data is not None:
            for image_file in images_data:
                img_instance = Image.objects.create(image=image_file)
                instance.images.add(img_instance)
        return instance
