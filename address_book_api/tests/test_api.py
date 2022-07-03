from collections import OrderedDict

from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
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
        self.test_user2.postal_addresses.add(self.shared_postal_address)

        self.client = APIClient()
        self.client.login(username="testuser1", password="notarealpassword")

    def test_view_address(self):
        """View user's associated addresses"""
        response = self.client.get("/api/v1/addressbook")
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

    def test_create_address_post(self):
        """Should be able to create address
        Should return a 400 error if same addresses is added multiple times
        """
        count = self.test_user1.postal_addresses.count()
        response = self.client.post(
            "/api/v1/addressbook",
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
            "/api/v1/addressbook",
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

        response = self.client.get("/api/v1/addressbook")
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

    def test_delete_address(self):

        count = self.test_user1.postal_addresses.count()
        address1_id = self.address1.id
        self.assertTrue(
            self.test_user1.postal_addresses.filter(id=address1_id).exists()
        )

        self.assertEqual(
            self.client.delete(f"/api/v1/addressbook{address1_id}/").status_code, 204
        )
        self.assertFalse(
            self.test_user1.postal_addresses.filter(id=address1_id).exists()
        )
        # Check that deletion has also occurred on PostalAddress table
        self.assertFalse(PostalAddress.objects.filter(id=address1_id).exists())
        self.assertEqual(count - 1, self.test_user1.postal_addresses.count())

        # Attempt to delete a resource that doesn't exist

        self.assertEqual(
            self.client.delete(f"/api/v1/addressbook{address1_id}/").status_code, 404
        )

        self.assertEqual(
            self.client.delete(f"/api/v1/addressbook333/").status_code, 404
        )

        # Attempt to delete addresses that are not assigned to you
        self.assertEqual(
            self.client.delete(f"/api/v1/addressbook{self.address4.id}/").status_code,
            404,
        )
        # Attempt to delete shared address
        self.assertEqual(
            self.client.delete(
                f"/api/v1/addressbook{self.shared_postal_address.id}/"
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
        self.assertEqual(self.client.get("/api/v1/addressbook").status_code, 401)

    def test_user_login(self):
        """
        Test: User should be able to login

        """

        self.client.login(username="testuser1", password="notarealpassword")
        self.assertEqual(self.client.get("/api/v1/addressbook").status_code, 200)

    def test_user_logout(self):
        """
        Test: User should be able to logout

        """
        self.client.login(username="testuser1", password="notarealpassword")
        self.assertEqual(self.client.get("/api/v1/addressbook").status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get("/api/v1/addressbook").status_code, 401)

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
        self.assertEqual(client.get("/api/v1/addressbook").status_code, 200)
