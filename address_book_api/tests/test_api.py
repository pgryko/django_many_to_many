from collections import OrderedDict

from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from address_book_api.models import AddressUser, PostalAddress


class AddressAPITestCase(TestCase):
    def setUp(self) -> None:
        self.test_user1 = AddressUser.objects.create_user(
            username="testuser1", password="notarealpassword"
        )

        self.address1 = PostalAddress.objects.get_or_create(
            address1="25 SomeDay Road",
            address2="testuser1only",
            zip_code="728wye",
            city="London",
            country="GBR",
        )[0]

        self.test_user1.postal_addresses.add(self.address1)
        self.address2 = PostalAddress.objects.get_or_create(
            address1="14 SomeDay Road",
            address2="testuser1only",
            zip_code="728wye",
            city="London",
            country="GBR",
        )[0]
        self.test_user1.postal_addresses.add(self.address2)

        self.test_user2 = AddressUser.objects.create_user(
            username="testuser2", password="notarealpassword"
        )

        self.address3 = PostalAddress.objects.get_or_create(
            address1="64 SomeDay Road",
            address2="testuser2only",
            zip_code="22kss",
            city="York",
            country="GBR",
        )[0]
        self.test_user2.postal_addresses.add(self.address3)
        self.address4 = PostalAddress.objects.get_or_create(
            address1="54 Askel road",
            address2="testuser2only",
            zip_code="fds0l2",
            city="York",
            country="GBR",
        )[0]
        self.test_user2.postal_addresses.add(self.address4)

        # Create a postal address that will be shared by user 1 and 2
        self.shared_postal_address = PostalAddress.objects.get_or_create(
            address1="Our Coworking space",
            address2="testuser1andtestuser2",
            zip_code="reqaw2",
            city="Cambridge",
            country="GBR",
        )[0]

        self.test_user1.postal_addresses.add(self.shared_postal_address)
        self.test_user1.save()
        self.test_user2.postal_addresses.add(self.shared_postal_address)
        self.test_user2.save()

        self.client = APIClient()
        self.client.login(username="testuser1", password="notarealpassword")

    def test_view_address(self):
        """View user's associated addresses"""
        response = self.client.get(reverse("postaladdress-list"))
        self.assertCountEqual(
            response.data,
            [
                OrderedDict(
                    [
                        ("id", self.address1.id),
                        ("address1", "25 SomeDay Road"),
                        ("address2", "testuser1only"),
                        ("zip_code", "728wye"),
                        ("city", "London"),
                        ("country", "GBR"),
                    ]
                ),
                OrderedDict(
                    [
                        ("id", self.address2.id),
                        ("address1", "14 SomeDay Road"),
                        ("address2", "testuser1only"),
                        ("zip_code", "728wye"),
                        ("city", "London"),
                        ("country", "GBR"),
                    ]
                ),
                OrderedDict(
                    [
                        ("id", self.shared_postal_address.id),
                        ("address1", "Our Coworking space"),
                        ("address2", "testuser1andtestuser2"),
                        ("zip_code", "reqaw2"),
                        ("city", "Cambridge"),
                        ("country", "GBR"),
                    ]
                ),
            ],
        )

    def test_view_address_filter(self):
        """View user's associated addresses, and filter by params
        Note, we've only tested filtering by a single param, if we wanted to be through
        we should test filtering with other params works
        """
        response = self.client.get(f"{reverse('postaladdress-list')}?zip_code=728wye")
        self.assertCountEqual(
            response.data,
            OrderedDict(
                [
                    ("count", 2),
                    ("next", None),
                    ("previous", None),
                    (
                        "results",
                        [
                            OrderedDict(
                                [
                                    ("id", self.address1.id),
                                    ("address1", "25 SomeDay Road"),
                                    ("address2", "testuser1only"),
                                    ("zip_code", "728wye"),
                                    ("city", "London"),
                                    ("country", "GBR"),
                                ]
                            ),
                            OrderedDict(
                                [
                                    ("id", self.address2.id),
                                    ("address1", "14 SomeDay Road"),
                                    ("address2", "testuser1only"),
                                    ("zip_code", "728wye"),
                                    ("city", "London"),
                                    ("country", "GBR"),
                                ]
                            ),
                        ],
                    ),
                ]
            ),
        )

    def test_view_address_pagination(self):
        """Test pagination for batch get"""
        response = self.client.get(f"{reverse('postaladdress-list')}?limit=2&offset=2")
        self.assertCountEqual(
            response.data,
            OrderedDict(
                [
                    ("count", 3),
                    ("next", "http://testserver/api/v1/addressbook/?limit=2&offset=2"),
                    ("previous", None),
                    (
                        "results",
                        [
                            OrderedDict(
                                [
                                    ("id", self.address1.id),
                                    ("address1", "25 SomeDay Road"),
                                    ("address2", "testuser1only"),
                                    ("zip_code", "728wye"),
                                    ("city", "London"),
                                    ("country", "GBR"),
                                ]
                            ),
                            OrderedDict(
                                [
                                    ("id", self.address2.id),
                                    ("address1", "14 SomeDay Road"),
                                    ("address2", "testuser1only"),
                                    ("zip_code", "728wye"),
                                    ("city", "London"),
                                    ("country", "GBR"),
                                ]
                            ),
                        ],
                    ),
                ]
            ),
        )
        response = self.client.get(f"{reverse('postaladdress-list')}?limit=2")
        self.assertCountEqual(
            response.data,
            OrderedDict(
                [
                    ("count", 3),
                    ("next", None),
                    ("previous", None),
                    (
                        "results",
                        [
                            OrderedDict(
                                [
                                    ("id", self.shared_postal_address.id),
                                    ("address1", "Our Coworking space"),
                                    ("address2", "testuser1andtestuser2"),
                                    ("zip_code", "reqaw2"),
                                    ("city", "Cambridge"),
                                    ("country", "GBR"),
                                ]
                            ),
                        ],
                    ),
                ]
            ),
        )

    def test_create_address_post(self):
        """Should be able to create address
        Should return a 400 error if same addresses is added multiple times
        """
        count = self.test_user1.postal_addresses.count()
        response = self.client.post(
            reverse("postaladdress-list"),
            {
                "address1": "Addressssss 1",
                "address2": "Second line",
                "zip_code": "90l2s",
                "city": "Cambridge",
                "country": "GBR",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            self.test_user1.postal_addresses.filter(address1="Addressssss 1").exists()
        )

        self.assertEqual(count + 1, self.test_user1.postal_addresses.count())

        response = self.client.post(
            reverse("postaladdress-list"),
            {
                "address1": "Addressssss 1",
                "address2": "Second line",
                "zip_code": "90l2s",
                "city": "Cambridge",
                "country": "GBR",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertDictEqual(
            response.data,
            {
                "non_field_errors": [
                    ErrorDetail(
                        string="The fields address1, address2, zip_code, city, country must make a unique set.",
                        code="unique",
                    )
                ]
            },
        )

        # Check to make sure that count is still the same (only one added)
        self.assertEqual(count + 1, self.test_user1.postal_addresses.count())

        # And that view address returns added new address
        # Technically this is coupling between the previous test (test_view_address)
        # but I prefer to be a little paranoid and check explicitly

        response = self.client.get(reverse("postaladdress-list"))
        self.assertCountEqual(
            response.data,
            [
                OrderedDict(
                    [
                        ("id", self.address1.id),
                        ("address1", "25 SomeDay Road"),
                        ("address2", "testuser1only"),
                        ("zip_code", "728wye"),
                        ("city", "London"),
                        ("country", "GBR"),
                    ]
                ),
                OrderedDict(
                    [
                        ("id", self.address2.id),
                        ("address1", "14 SomeDay Road"),
                        ("address2", "testuser1only"),
                        ("zip_code", "728wye"),
                        ("city", "London"),
                        ("country", "GBR"),
                    ]
                ),
                OrderedDict(
                    [
                        ("id", self.shared_postal_address.id),
                        ("address1", "Our Coworking space"),
                        ("address2", "testuser1andtestuser2"),
                        ("zip_code", "reqaw2"),
                        ("city", "Cambridge"),
                        ("country", "GBR"),
                    ]
                ),
                OrderedDict(
                    [
                        (
                            "id",
                            self.test_user1.postal_addresses.get(
                                address1="Addressssss 1"
                            ).id,
                        ),
                        ("address1", "Addressssss 1"),
                        ("address2", "Second line"),
                        ("zip_code", "90l2s"),
                        ("city", "Cambridge"),
                        ("country", "GBR"),
                    ]
                ),
            ],
        )

    def test_patch(self):
        """Should correctly update an address"""
        response = self.client.get(reverse("postaladdress-list"))
        self.assertCountEqual(
            response.data,
            OrderedDict(
                [
                    ("count", 4),
                    ("next", None),
                    ("previous", None),
                    (
                        "results",
                        [
                            OrderedDict(
                                [
                                    ("id", self.address1.id),
                                    ("address1", "25 SomeDay Road"),
                                    ("address2", "testuser1only"),
                                    ("zip_code", "728wye"),
                                    ("city", "London"),
                                    ("country", "GBR"),
                                ]
                            ),
                            OrderedDict(
                                [
                                    ("id", self.address2.id),
                                    ("address1", "14 SomeDay Road"),
                                    ("address2", "testuser1only"),
                                    ("zip_code", "728wye"),
                                    ("city", "London"),
                                    ("country", "GBR"),
                                ]
                            ),
                            OrderedDict(
                                [
                                    ("id", self.shared_postal_address.id),
                                    ("address1", "Our Coworking space"),
                                    ("address2", "testuser1andtestuser2"),
                                    ("zip_code", "reqaw2"),
                                    ("city", "Cambridge"),
                                    ("country", "GBR"),
                                ]
                            ),
                        ],
                    ),
                ]
            ),
        )

        response = self.client.patch(
            f"{reverse('postaladdress-list')}/{self.address1.id}/",
            {
                "address1": "Addressssss 1",
                "address2": "Second line",
                "zip_code": "90l2s",
                "city": "Cambridge",
                "country": "GBR",
            },
        )
        self.assertEqual(response.status_code, 200)

        # Test that it's been correctly updated
        response = self.client.get(f"{reverse('postaladdress-list')}/{self.address1.id}/")
        self.assertCountEqual(
            response.data,
            {
                "id": self.address1.id,
                "address1": "Addressssss 1",
                "address2": "Second line",
                "zip_code": "90l2s",
                "city": "Cambridge",
                "country": "GBR",
            },
        )

        # Test that unique constraints hold, i.e. you can't update to something that already exists
        response = self.client.patch(
            f"/{reverse('postaladdress-list')}/{self.address1.id}/",
            {
                "address1": "14 SomeDay Road",
                "address2": "testuser1only",
                "zip_code": "728wye",
                "city": "London",
                "country": "GBR",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertCountEqual(
            response.data,
            {
                "non_field_errors": [
                    ErrorDetail(
                        string="The fields address1, address2, zip_code, city, country, user must make a unique set.",
                        code="unique",
                    )
                ]
            },
        )

    def test_delete_address(self):

        count = self.test_user1.postal_addresses.count()
        address1_id = self.address1.id
        self.assertTrue(
            self.test_user1.postal_addresses.filter(id=address1_id).exists()
        )

        self.assertEqual(
            self.client.delete(f"{reverse('postaladdress-list')}/{address1_id}").status_code, 204
        )
        self.assertFalse(
            self.test_user1.postal_addresses.filter(id=address1_id).exists()
        )
        # Check that deletion has also occurred on PostalAddress table
        self.assertFalse(PostalAddress.objects.filter(id=address1_id).exists())
        self.assertEqual(count - 1, self.test_user1.postal_addresses.count())

        # Attempt to delete a resource that doesn't exist

        self.assertEqual(
            self.client.delete(f"{reverse('postaladdress-list')}/{address1_id}").status_code, 404
        )

        self.assertEqual(
            self.client.delete(f"{reverse('postaladdress-list')}/333/").status_code, 404
        )

        # Attempt to delete addresses that are not assigned to you
        self.assertEqual(
            self.client.delete(f"{reverse('postaladdress-list')}/{self.address4.id}").status_code,
            404,
        )
        # Attempt to delete shared address
        self.assertEqual(
            self.client.delete(
                f"{reverse('postaladdress-list')}/{self.shared_postal_address.id}"
            ).status_code,
            204,
        )
        self.assertFalse(
            self.test_user1.postal_addresses.filter(
                id=self.shared_postal_address.id
            ).exists()
        )
        # Check that deletion has NOT occurred on PostalAddress table as It's still referenced but user2
        self.assertTrue(
            PostalAddress.objects.filter(id=self.shared_postal_address.id).exists()
        )

    def test_delete_address_batch(self):
        count = self.test_user1.postal_addresses.count()
        address1_id = self.address1.id
        address2_id = self.address2.id

        self.assertTrue(PostalAddress.objects.filter(id=address1_id).exists())
        self.assertTrue(PostalAddress.objects.filter(id=address2_id).exists())

        self.assertEqual(
            self.client.delete(
                f"{reverse('postaladdress-list')}/batch/?ids={address1_id},{address2_id}"
            ).status_code,
            204,
        )
        self.assertFalse(PostalAddress.objects.filter(id=address1_id).exists())
        self.assertFalse(PostalAddress.objects.filter(id=address2_id).exists())
        self.assertEqual(
            count - 2, PostalAddress.objects.filter(user=self.test_user1).count()
        )

        # Test that you can't delete someone else's PostalAddress
        self.assertEqual(
            self.client.delete(
                f"{reverse('postaladdress-list')}/batch/?ids={self.address3.id}"
            ).status_code,
            404,
        )

        self.assertTrue(PostalAddress.objects.filter(id=self.address3.id).exists())

    def test_delete_address_batch_transactional(self):
        """Test that when multiple addresses are sent for deletion, that if one object
        is not found, the whole operation fails and no addresses are deleted

        """

        address1_id = self.address1.id
        address2_id = self.address2.id

        self.assertTrue(PostalAddress.objects.filter(id=address1_id).exists())
        self.assertTrue(PostalAddress.objects.filter(id=address2_id).exists())

        # Expect to fail as address3 is not owned by logged in user
        self.assertEqual(
            self.client.delete(
                f"{reverse('postaladdress-list')}/batch/?ids={address1_id},{self.address3.id}"
            ).status_code,
            404,
        )

        self.assertTrue(PostalAddress.objects.filter(id=address1_id).exists())
        self.assertTrue(PostalAddress.objects.filter(id=self.address3.id).exists())


class AuthenticationTestCase(TestCase):
    def setUp(self) -> None:
        self.test_user = AddressUser.objects.create_user(
            username="testuser1", password="notarealpassword"
        )
        self.client = APIClient()

    def test_address_authentication(self):
        """
        Test: Address requires user to be authenticated to view
        Addresses with from other users should not be visible

        """
        self.assertEqual(self.client.get(reverse("postaladdress-list")).status_code, 401)

    def test_user_login(self):
        """
        Test: User should be able to login

        """

        self.client.login(username="testuser1", password="notarealpassword")
        self.assertEqual(self.client.get(reverse("postaladdress-list")).status_code, 200)

    def test_user_logout(self):
        """
        Test: User should be able to logout

        """
        self.client.login(username="testuser1", password="notarealpassword")
        self.assertEqual(self.client.get(reverse("postaladdress-list")).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("postaladdress-list")).status_code, 401)

    def test_user_api_token(self):
        """
        Test: Test Authentication via an api token
        """

        response = self.client.post(
            "/api-token-auth/",
            {"username": "testuser1", "password": "notarealpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]
        client = APIClient(HTTP_AUTHORIZATION="Token " + token)
        self.assertEqual(client.get(reverse("postaladdress-list")).status_code, 200)
