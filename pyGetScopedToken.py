#!/usr/bin/env python3

import requests
import json
import os
from urlparse import urlparse, urlunparse, urljoin

# from urllib.parse import urlparse, urlunparse, urljoin


def get_OIDC_Token(checkin_auth_url, client_id, client_secret, refresh_token):
    """ Get an OIDC token from the EGI AAI Check-In service"""

    # Creating the paylod for the request
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "openid email profile",
    }

    curl = requests.post(
        url=checkin_auth_url, auth=(client_id, client_secret), data=payload
    )
    data = curl.json()

    # Server response
    return data["access_token"]


def get_unscoped_Token(os_auth_url, access_token):
    """ Retrieve an uscoped token from OpenStack Keystone """

    url = get_keystone_url(
        os_auth_url, "/v3/OS-FEDERATION/identity_providers/egi.eu/protocols/openid/auth"
    )

    curl = requests.post(url, headers={"Authorization": "Bearer %s" % access_token})

    return curl.headers["X-Subject-Token"]


def get_keystone_url(os_auth_url, path):
    """ Get Keystone URL """

    url = urlparse(os_auth_url)
    prefix = url.path.rstrip("/")
    if prefix.endswith("v2.0") or prefix.endswith("v3"):
        prefix = os.path.dirname(prefix)

    path = os.path.join(prefix, path)

    return urlunparse((url[0], url[1], path, url[3], url[4], url[5]))


def get_scoped_Token(os_auth_url, os_project_id, unscoped_token):
    """ Get scoped token """

    url = get_keystone_url(os_auth_url, "/v3/auth/tokens")

    token_body = {
        "auth": {
            "identity": {"methods": ["token"], "token": {"id": unscoped_token}},
            "scope": {"project": {"id": os_project_id}},
        }
    }

    r = requests.post(
        url, headers={"content-type": "application/json"}, data=json.dumps(token_body)
    )

    return r.headers["X-Subject-Token"]
