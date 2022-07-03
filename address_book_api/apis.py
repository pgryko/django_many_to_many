from django.contrib.auth.models import User
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, authentication, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django_filters import rest_framework as filters

from address_book_api.models import AddressUser, PostalAddress
from address_book_api.serialisers import AddressUserSerializer, PostalAddressSerializer


class PostalAddressFilter(filters.FilterSet):
    class Meta:
        model = PostalAddress
        fields = ["address1", "address2", "zip_code", "city", "country", "id"]

class AddressUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows current user
    to be viewed, created or deleted

    Used by Django admin interface
    """

    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
    ]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = AddressUserSerializer

    def get_queryset(self):
        username = self.request.user
        user = User.objects.get(username=username)
        queryset = AddressUser.objects.get(user=user)
        return queryset


class PostalAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows addresses associated with current user
    to be viewed, created or deleted
    """

    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
    ]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]

    serializer_class = PostalAddressSerializer

    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        username = self.request.user
        user = User.objects.get(username=username)
        if not AddressUser.objects.filter(user=user).exists():
            raise PermissionDenied(detail="User is not an address book user")

        return AddressUser.objects.get(user=user).postal_addresses

    def perform_create(self, serializer):
        """Overwrite preform_create for view, to associate PostalAddress with AddressUser
        after PostalAddress has been saved
        """
        saved_address = serializer.save()

        username = self.request.user
        user = User.objects.get(username=username)

        AddressUser.objects.get(user=user).postal_addresses.add(saved_address)

    def destroy(self, request, *args, **kwargs):
        """Overwrite destroy so that if address is referenced by other AddressUsers, it is only removed
        from the ManyToMany model and not deleted. We this by using delete member function that's part of
        AddressUser, instead of Postal

        """
        postal_address_instance = self.get_object()

        user = User.objects.get(username=self.request.user)

        # This will remove the Postal Address from AddressUser and only
        # delete the Postal Address if it's not used by anything else
        AddressUser.objects.get(user=user).postal_addresses.remove(
            postal_address_instance
        )

        if not AddressUser.objects.filter(
            postal_addresses=postal_address_instance.id
        ).exists():
            # If it's not associated else where, remove it
            self.perform_destroy(postal_address_instance)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[OpenApiParameter("ids", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        description="Comma seperated list of PostalAddress ids, e.g. batch/?ids=1,2,4",
    )
    @action(
        detail=False,
        methods=["delete"],
        name="batch_delete",
    )
    def batch(self, request):
        ids = request.query_params.get("ids")
        user = User.objects.get(username=self.request.user)

        obj_list = []
        for identifier in ids.split(","):
            obj_list.append(get_object_or_404(PostalAddress, id=identifier, user=user))

        # We only want to delete to occur if all ids have matched
        [x.delete() for x in obj_list]

        return Response(status=status.HTTP_204_NO_CONTENT)

