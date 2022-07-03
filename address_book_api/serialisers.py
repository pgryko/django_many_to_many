from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from address_book_api.models import AddressUser, PostalAddress


class PostalAddressSerializer(serializers.ModelSerializer):
    """Serializer for PostalAddress
    Note: the default Serializer.save() will not update the association
    AddressUser -> PostalAddressSerializer
    Currently this is set in the api view
    """

    class Meta:
        model = PostalAddress
        fields = "__all__"
        read_only = ("id",)

    # We've added the constraint to the model
    # but for good measure we'll also add it to the serializer validator
    # This automatically returns the correct 400 error
    validators = [
        UniqueTogetherValidator(
            queryset=PostalAddress.objects.all(),
            fields=["address1", "address2", "zip_code", "city", "country"],
        )
    ]


class AddressUserSerializer(serializers.HyperlinkedModelSerializer):
    postal_addresses = PostalAddressSerializer(many=True)

    postal_addresses_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        # write_only=True,
        source="postal_addresses",  # just to make it looks a little bit better
        queryset=PostalAddress.objects.all(),
    )

    class Meta:
        model = AddressUser
        fields = "__all__"
