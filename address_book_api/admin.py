from django.contrib import admin

from address_book_api.models import AddressUser, PostalAddress

# Register your models here.

# Re-register UserAdmin
admin.site.register(AddressUser)
admin.site.register(PostalAddress)
