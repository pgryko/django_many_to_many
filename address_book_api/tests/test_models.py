from django.test import TestCase
from django.db.utils import IntegrityError
from address_book_api.models import AddressUser, PostalAddress


# Create your tests here.


class PostalAddressTestCase(TestCase):
    def test_creation(self):
        # Should not throw
        address1 = PostalAddress.objects.create(
            address1="25 SomeDay Road",
            zip_code="728wye",
            city="London",
            country="GBR",
        )
        # Check that uniqueness constraint holds
        # Spec: User will not be able to add a duplicated address to their account
        self.assertRaises(
            IntegrityError,
            PostalAddress.objects.create,
            address1="25 SomeDay Road",
            zip_code="728wye",
            city="London",
            country="GBR",
        )
        # Todo: Add test of all permutations of nullable zip_code, city, country


class AddressUserTestCase(TestCase):
    def test_create_address_user(self):
        """Simple test cases for addressuser model
        Spec: User is able to create a new address
              User will not be able to add a duplicated address to their account
              User can have multiple addresses
              User is able to filter retrieved addresses using request parameters

        """
        user1 = AddressUser.objects.create_user(username="testuser")

        address1 = PostalAddress.objects.create(
            address1="25 SomeDay Road", zip_code="728wye", city="London", country="GBR"
        )

        user1.postal_addresses.add(address1)
        self.assertEqual(user1.postal_addresses.first(), address1)

        address2 = PostalAddress.objects.create(
            address1="14 SomeDay Road", zip_code="728wye", city="London", country="GBR"
        )

        user1.postal_addresses.add(address2)

        self.assertIn(address1, user1.postal_addresses.all())
        self.assertIn(address2, user1.postal_addresses.all())
        self.assertEqual(2, len(user1.postal_addresses.all()))

        # Spec: User will not be able to add a duplicated address to their account
        user1.postal_addresses.add(address1)
        # Check that there are still only 2 addresses
        self.assertEqual(2, len(user1.postal_addresses.all()))


def test_delete_address_user(self):
    """Test correct handling of deleting address user
    Spec: When address user is deleted, associated user account should
    be deleted. For associated addresses - If the address is used by multiple
    users, keep the address. Otherwise delete it

    """
    user1 = AddressUser.objects.create_user(user="testuser1")
    user2 = AddressUser.objects.create_user(user="testuser2")

    address1 = PostalAddress.objects.create(
        address1="25 SomeDay Road", zip_code="728wye", city="London", country="GBR"
    )
    address2 = PostalAddress.objects.create(
        address1="14 SomeDay Road", zip_code="728wye", city="London", country="GBR"
    )
    shared_address = PostalAddress.objects.create(
        address1="30 Day Road", zip_code="eww", city="London", country="GBR"
    )
    user1.postal_addresses.add(address1)
    user1.postal_addresses.add(address2)
    user1.postal_addresses.add(shared_address)
    user2.postal_addresses.add(shared_address)

    self.assertIn(address1, user1.postal_addresses.all())
    self.assertIn(address2, user1.postal_addresses.all())
    self.assertIn(shared_address, user1.postal_addresses.all())
    self.assertIn(shared_address, user2.postal_addresses.all())

    # Test deletion of a single address
    user1.postal_addresses.remove(address1)
    self.assertNotIn(address1, user1.postal_addresses.all())

    # Test deletion of a shared address
    user1.postal_addresses.remove(shared_address)
    self.assertNotIn(shared_address, user1.postal_addresses.all())
    # Should still exist for user 2
    self.assertIn(shared_address, user2.postal_addresses.all())
    self.assertTrue(PostalAddress.objects.filter(id=shared_address.id).exists())
