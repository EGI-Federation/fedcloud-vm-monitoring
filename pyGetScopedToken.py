#!/usr/bin/env python3.9
#
#  Copyright 2021 EGI Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import requests
import json
import os
from urllib.parse import urlparse, urlunparse, urljoin

__author__ = "Giuseppe LA ROCCA"
__email__ = "giuseppe.larocca@egi.eu"
__version__ = "$Revision: 1.0.0"
__date__ = "$Date: 05/06/2021 15:46:33"
__copyright__ = "Copyright (c) 2021 EGI Foundation"
__license__ = "Apache Licence v2.0"


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


def get_unscoped_Token(os_auth_url, access_token, protocol):
    """ Retrieve an unscoped token from OpenStack Keystone """

    if protocol == "openid":
        url = get_keystone_url(
            os_auth_url,
            "/v3/OS-FEDERATION/identity_providers/egi.eu/protocols/openid/auth",
        )
    else:
        url = get_keystone_url(
            os_auth_url,
            "/v3/OS-FEDERATION/identity_providers/egi.eu/protocols/oidc/auth",
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
