from django.contrib.auth.models import User

from address_book_api.models import AddressUser, PostalAddress

"""
Generates dummy user data for development purposes.

"""


def run():
    # Create a testuser1 and associated 2 addresses with them
    user1 = User.objects.filter(username="testuser1").first()
    if not user1:
        user1 = AddressUser.objects.create_user(
            username="testuser1", password="notarealpassword"
        )
    else:
        user1 = AddressUser.objects.get(user=user1)

    user1.postal_addresses.add(
        PostalAddress.objects.get_or_create(
            address1="25 SomeDay Road",
            address2="testuser1only",
            zip_code="728wye",
            city="London",
            country="GBR",
        )[0]
    )
    user1.postal_addresses.add(
        PostalAddress.objects.get_or_create(
            address1="14 SomeDay Road",
            address2="testuser1only",
            zip_code="728wye",
            city="London",
            country="GBR",
        )[0]
    )
    # Create a testuser2 and associated 2 addresses with them
    user2 = User.objects.filter(username="testuser2")
    if not user2.exists():
        user2 = AddressUser.objects.create_user(username="testuser2")
    else:
        user2 = AddressUser.objects.get(user=user2)

    user2.postal_addresses.add(
        PostalAddress.objects.get_or_create(
            address1="64 SomeDay Road",
            address2="testuser2only",
            zip_code="22kss",
            city="York",
            country="GBR",
        )[0]
    )
    user2.postal_addresses.add(
        PostalAddress.objects.get_or_create(
            address1="54 Askel road",
            address2="testuser2only",
            zip_code="fds0l2",
            city="York",
            country="GBR",
        )[0]
    )

    # Create a postal address that will be shared by user 1 and 2
    shared_postal_address = PostalAddress.objects.get_or_create(
        address1="Our Coworking space",
        address2="testuser1andtestuser2",
        zip_code="reqaw2",
        city="Cambridge",
        country="GBR",
    )[0]

    user1.postal_addresses.add(shared_postal_address)
    user2.postal_addresses.add(shared_postal_address)

    # Create unassociated user and postaladdress
    if not User.objects.filter(username="testuser3Unassociated").exists():
        AddressUser.objects.create_user(username="testuser3Unassociated")

    PostalAddress.objects.get_or_create(
        address1="903 Keeton",
        address2="NoAssociatedUsers",
        zip_code="wqew",
        city="Manchester",
        country="GBR",
    )
