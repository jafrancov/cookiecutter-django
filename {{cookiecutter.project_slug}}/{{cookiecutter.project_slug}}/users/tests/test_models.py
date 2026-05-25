from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from {{ cookiecutter.project_slug }}.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from {{ cookiecutter.project_slug }}.users.models import User


def test_user_get_absolute_url(user: User):
    {%- if cookiecutter.username_type == "email" %}
    assert user.get_absolute_url() == f"/users/{user.pk}/"
    {%- else %}
    assert user.get_absolute_url() == f"/users/{user.username}/"
    {%- endif %}


@pytest.mark.django_db
class TestUserSave:
    def test_first_name_is_stripped_on_save(self):
        user = UserFactory.create(first_name="  John  ")
        assert user.first_name == "John"

    def test_last_name_is_stripped_on_save(self):
        user = UserFactory.create(last_name="  Doe  ")
        assert user.last_name == "Doe"

    def test_email_is_lowercased_on_save(self):
        user = UserFactory.create(email="John.Doe@Example.COM")
        assert user.email == "john.doe@example.com"

    def test_first_name_and_last_name_are_persisted(self):
        user = UserFactory.create(first_name="Jane", last_name="Smith")
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"

