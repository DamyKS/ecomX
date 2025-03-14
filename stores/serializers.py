from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


# class StoreGetSerializer(serializers.ModelSerializer):
#     owner = serializers.StringRelatedField()

#     class Meta:
#         model = Store
#         fields = "__all__"
#         read_only_fields = ["owner", "id", "created_at"]


class StoreGetSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    # Override hero_image to return the full URL
    hero_image = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ["owner", "id", "created_at"]

    def get_hero_image(self, obj):
        if obj.hero_image:
            url = obj.hero_image.url
            # Use the request context to build an absolute URL
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
