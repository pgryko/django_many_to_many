from django.db import models
from django.contrib.auth.models import User
from django.db.models.constraints import UniqueConstraint
from django.db.models import Q
import iso3166

# Create your models here.

# Postal address can be a mess
# https://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/
# We are not going to do detailed validation of uniqueness here
# we could use https://www.geonames.org/ via https://pypi.org/project/django-cities-light/
# or validate against google maps api https://github.com/furious-luke/django-address
from rest_framework.validators import UniqueTogetherValidator


class PostalAddress(models.Model):
    # Technically address 1 and country are the only strict requirements
    # you can live outside a city, without a zip code or have a short address
    # I'm going to assume you don't live in the Sea or in earths low orbit
    address1 = models.CharField(
        "Address line 1",
        max_length=1024,
        null=False,
    )

    address2 = models.CharField("Address line 2", max_length=1024, null=True)

    zip_code = models.CharField(
        "ZIP / Postal code",
        max_length=12,
        null=True,
    )

    # TODO: add validation so that city and country are consistent
    city = models.CharField(
        "City",
        max_length=1024,
        null=True,
    )

    country = models.CharField(
        "Country",
        max_length=3,
        choices=[(k, v.name) for (k, v) in iso3166.countries_by_alpha3.items()],
        null=False,
    )

    def __str__(self):
        return (
            self.address1
            + " "
            + self.address2
            + " "
            + self.zip_code
            + " "
            + self.city
            + " "
            + self.country
        )

    class Meta:
        verbose_name = "Postal Address"
        verbose_name_plural = "Postal Addresses"
        constraints = [
            # As address2 is optional (null=True)
            UniqueConstraint(
                fields=["address1", "address2", "zip_code", "city", "country"],
                name="unique_with_all",
            ),
            UniqueConstraint(
                fields=["address1", "country"],
                condition=Q(address2=None, zip_code=None, city=None),
                name="unique_without_address2_zip_code_city",
            ),
            UniqueConstraint(
                fields=["address1", "address2", "country"],
                condition=Q(zip_code=None, city=None),
                name="unique_without_zip_code_city",
            ),
            UniqueConstraint(
                fields=["address1", "address2", "zip_code", "country"],
                condition=Q(city=None),
                name="unique_without_city",
            ),
            UniqueConstraint(
                fields=["address1", "zip_code", "country"],
                condition=Q(address2=None),
                name="unique_without_address2",
            ),
            UniqueConstraint(
                fields=["address1", "address2", "zip_code", "country"],
                condition=Q(zip_code=None),
                name="unique_without_zip_code",
            ),
            UniqueConstraint(
                fields=["address1", "city", "country"],
                condition=Q(address2=None, zip_code=None),
                name="unique_without_address2_zip_code",
            ),
            UniqueConstraint(
                fields=["address1", "zip_code", "country"],
                condition=Q(address2=None, city=None),
                name="unique_without_address2_city",
            ),
        ]


class AddressUserManager(models.Manager):
    """Add additonal method to address user to emulate create_user behaviour
    from django.contrib.auth.models.User
    """

    def create_user(*args, **kwargs):
        new_user = User.objects.create_user(**kwargs)

        return AddressUser.objects.create(user=new_user)


class AddressUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    postal_addresses = models.ManyToManyField(
        PostalAddress, related_name="postaladdresses"
    )

    @property
    def username(self):
        return self.username

    def __str__(self):
        postal_addresses = ", ".join(str(seg) for seg in self.postal_addresses.all())
        return str(self.user) + ": " + str(postal_addresses)

    objects = AddressUserManager()
