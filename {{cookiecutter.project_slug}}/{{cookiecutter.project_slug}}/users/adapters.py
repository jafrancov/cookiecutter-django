from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def pre_social_login(self, request, sociallogin):
        # social account already exists, so this is just a login
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address
        if not sociallogin.email_addresses:
            return

        # find the first verified email that we get from this sociallogin
        verified_email = None
        for email in sociallogin.email_addresses:
            if email.verified:
                verified_email = email
                break

        # no verified emails found, nothing more to do
        if not verified_email:
            return

        if request.user.is_authenticated and request.user.email != verified_email.email:
            # Obtener el nombre del proveedor social de manera más segura
            provider_name = sociallogin.account.provider.capitalize()
            messages.error(
                request,
                (
                    f"No es posible enlazar tu cuenta de {provider_name}, "
                    "ya que no coincide con tu correo en esta plataforma."
                ),
            )
            raise ImmediateHttpResponse(redirect(reverse("socialaccount_connections")))

        # check if given email address already exists as a verified email on
        # an existing user's account
        try:
            existing_email = EmailAddress.objects.get(
                email__iexact=verified_email.email,
                verified=True
            )
        except EmailAddress.DoesNotExist:
            return

        # if it does, connect this new social login to the existing user
        sociallogin.connect(request, existing_email.user)
