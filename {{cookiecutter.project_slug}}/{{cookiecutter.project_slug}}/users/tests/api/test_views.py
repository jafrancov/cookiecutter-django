{% if cookiecutter.rest_api == 'DRF' -%}
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rest_framework.test import APIRequestFactory

from {{ cookiecutter.project_slug }}.users.api.views import UserViewSet

if TYPE_CHECKING:
    from {{ cookiecutter.project_slug }}.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore[call-arg]

        assert response.data == {
            {%- if cookiecutter.username_type == "username" %}
            "username": user.username,
            {%- endif %}
            "email": user.email,
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "url": f"http://testserver/api/users/{user.uuid}/",
        }
{%- elif cookiecutter.rest_api == 'Django Ninja' -%}
from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from {{ cookiecutter.project_slug }}.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from django.test import Client

    from {{ cookiecutter.project_slug }}.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory.create()


def test_list_users_as_anonymous_user(client: Client):
    response = client.get(reverse("api:list_users"))

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_list_users_as_authenticated_user(client: Client, user: User):
    client.force_login(user)
    # Another user, excluded from the response
    UserFactory.create()

    response = client.get(reverse("api:list_users"))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "uuid": user.uuid,
            "url": f"/api/users/{user.uuid}/",
            {%- if cookiecutter.username_type == "username" %}
            "username": user.username,
            {%- endif %}
        },
    ]
{%- if cookiecutter.username_type == "email" %}


def test_retrieve_current_user(client: Client, user: User):
    client.force_login(user)

    response = client.get(
        reverse("api:retrieve_current_user"),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "uuid": user.uuid,
        "url": f"/api/users/{user.uuid}/",
    }


def test_retrieve_user(client: Client, user: User):
    client.force_login(user)

    response = client.get(
        reverse("api:retrieve_user", kwargs={"uuid": user.uuid}),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "uuid": user.uuid,
        "url": f"/api/users/{user.uuid}/",
    }
{%- else %}


def test_retrieve_current_user(client: Client, user: User):
    client.force_login(user)

    response = client.get(
        reverse("api:retrieve_current_user"),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "uuid": user.uuid,
        "url": f"/api/users/{user.uuid}/",
        "username": user.username,
    }


def test_retrieve_user(client: Client, user: User):
    client.force_login(user)

    response = client.get(
        reverse("api:retrieve_user", kwargs={"uuid": user.uuid}),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "uuid": user.uuid,
        "url": f"/api/users/{user.uuid}/",
        "username": user.username,
    }
{%- endif %}


def test_retrieve_another_user(client: Client, user: User):
    client.force_login(user)
    user_2 = UserFactory.create()

    response = client.get(
        reverse("api:retrieve_user", kwargs={"uuid": user_2.uuid}),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Not Found"}


def test_update_current_user(client: Client):
    user = UserFactory.create(first_name="Old", last_name="Old")
    client.force_login(user)

    response = client.patch(
        reverse("api:update_current_user"),
        {%- if cookiecutter.username_type == "email" %}
        data='{"first_name": "New First Name", "last_name": "New Last Name"}',
        {%- else %}
        data='{"first_name": "New First Name", "last_name": "New Last Name", "username": "old"}',
        {%- endif %}
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == {
        "email": user.email,
        "first_name": "New First Name",
        "last_name": "New Last Name",
        "url": f"/api/users/{user.uuid}/",
        {%- if cookiecutter.username_type == "username" %}
        "username": "old",
        {%- endif %}
    }


{%- if cookiecutter.username_type == "email" %}


def test_update_user(client: Client):
    user = UserFactory.create(first_name="Old", last_name="Old")
    client.force_login(user)

    response = client.patch(
        reverse("api:update_user", kwargs={"uuid": user.uuid}),
        data='{"first_name": "New First Name", "last_name": "New Last Name"}',
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == {
        "email": user.email,
        "first_name": "New First Name",
        "last_name": "New Last Name"
        "url": f"/api/users/{user.uuid}/",
    }
{%- else %}


def test_update_user(client: Client):
    user = UserFactory.create(first_name="Old", last_name="Old", username="old")
    client.force_login(user)

    response = client.patch(
        reverse("api:update_user", kwargs={"username": "old"}),
        data='{"first_name": "New First Name", "last_name": "New Last Name", "username": "old"}',
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == {
        "email": user.email,
        "first_name": "New First Name",
        "last_name": "New Last Name"
        "url": f"/api/users/{user.uuid}/",
        "username": "old",
    }
{%- endif %}
{%- endif %}
