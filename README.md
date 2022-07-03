# Django Many-to-Many model API example

## Introduction

An example project demoing the use of a many-to-many model with django rest framework for creating an API capable of
handling postal address.

Note: this is *NOT* the correct way to handle postal addresses.
Postal address are best modeled by a many-to-one relationship, rather than the many-to-many written here.
I've left the code as it is, as a demo for handle many-to-many relationships in django
This project demos several aspects of django, specifically:
* Django Rest Framework
* Gitlab CI
* GithubCI
* SwaggerUI view

### Requirements
1. [x] User is able to create a new address 
    - [x] User will not be able to add a duplicated address to their account
2. [x] User is able to retrieve all their postal addresses 
    - [ ] User is able to retrieve a large number of address entries in a practical way
    - [ ] User is able to filter retrieved addresses using request parameters
3. [ ] User is able to update existing addresses 
4. [x] User is able to delete one 
    - [ ] User is able to delete multiple addresses
    - [x] User is able to authenticate with a username and a password
5. [x] User can log out

Additionally, added
- [x] Enabled token Based authentication
- [x] Added Swagger API webview

## Notes
- A user can have a large number of addresses
- A user can have addresses from any country
- A user's client can hold state (if necessary for certain endpoints)
- You must ensure the application can be run by another engineer with access to the repository
- You do not need to deploy this code to a server
- You should document any assumptions you make about the product, especially where you would have a question about it

Note: Currently Features that are incomplete
proper handling of Address Put, 
Bulk get pagination
Get filtering
# Technical

## Useful Commands

### Configuring environment

```bash
$ python3 -m venv venv; source venv/bin/activate; pip install -r requirements-dev.txt
```

### Running a dev server
```bash
$ python manage.py migrate
$ python manage.py runserver_plus
```

### Creating an admin user
Don't use in production
```bash
$ python manage.py shell --command="from django.contrib.auth.models import User
User.objects.create_superuser('a', 'a', 'a')"
```

### Load dummy data
Relies on django extensions - won't run unless in devmode (i.e. won't work in prod)
```bash
$ python manage.py runscript generate_dummy_data
```

### Running tests
```bash
$ python manage.py test
```

these should also work in parallel

```bash
$ python manage.py test --parallel
```

### Linting
Auto Lint using https://github.com/psf/black
```bash
$ black src
```

### Code quality
And check code quality using
```bash
$ pylint src
```

## Testing gitlab pipeline on localmachine

Its possible to install gitlab runner on your local machine and test the .gitlab-ci.yaml

```bash
$ gitlab-runner exec docker test\ django
```
