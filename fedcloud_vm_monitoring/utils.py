#!/usr/bin/env python3
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

import configparser
import json
import ldap3
import os
import urllib
from datetime import datetime
from ldap3 import Server, Connection, ALL
from urllib.request import Request, urlopen, ssl, socket
from urllib.error import URLError, HTTPError


__author__ = "Giuseppe LA ROCCA"
__email__ = "giuseppe.larocca@egi.eu"
__version__ = "$Revision: 1.0.5"
__date__ = "$Date: 23/09/2021 10:27:27"
__copyright__ = "Copyright (c) 2021 EGI Foundation"
__license__ = "Apache Licence v2.0"


def colourise(colour, text):
    """Colourise - colours text in shell."""
    """ Returns plain if colour doesn't exist """

    if colour == "black":
        return "\033[1;30m" + str(text) + "\033[1;m"
    if colour == "red":
        return "\033[1;31m" + str(text) + "\033[1;m"
    if colour == "green":
        return "\033[1;32m" + str(text) + "\033[1;m"
    if colour == "yellow":
        return "\033[1;33m" + str(text) + "\033[1;m"
    if colour == "blue":
        return "\033[1;34m" + str(text) + "\033[1;m"
    if colour == "magenta":
        return "\033[1;35m" + str(text) + "\033[1;m"
    if colour == "cyan":
        return "\033[1;36m" + str(text) + "\033[1;m"
    if colour == "gray":
        return "\033[1;37m" + str(text) + "\033[1;m"
    return str(text)


def highlight(colour, text):
    """Highlight - highlights text in shell."""
    """ Returns plain if colour doesn't exist. """

    if colour == "black":
        return "\033[1;40m" + str(text) + "\033[1;m"
    if colour == "red":
        return "\033[1;41m" + str(text) + "\033[1;m"
    if colour == "green":
        return "\033[1;42m" + str(text) + "\033[1;m"
    if colour == "yellow":
        return "\033[1;43m" + str(text) + "\033[1;m"
    if colour == "blue":
        return "\033[1;44m" + str(text) + "\033[1;m"
    if colour == "magenta":
        return "\033[1;45m" + str(text) + "\033[1;m"
    if colour == "cyan":
        return "\033[1;46m" + str(text) + "\033[1;m"
    if colour == "gray":
        return "\033[1;47m" + str(text) + "\033[1;m"
    return str(text)


def load_provider_settings(file):
    """Load cloud providers settings"""

    filename = "%s/%s" % (os.environ["PWD"], file)
    providers = []

    # Reading configuration file
    config = configparser.ConfigParser()
    config.read(filename)

    for section in config.sections():
        options = config.options(section)

        # Creation of the JSON file
        providers.append(
            {
                "provider": {
                    "ROC_name": config.get(section, "ROC_Name"),
                    "sitename": config.get(section, "Sitename"),
                    "hostname": config.get(section, "Hostname"),
                    "country": config.get(section, "Country"),
                    "identity": config.get(section, "Identity"),
                    "compute": config.get(section, "Compute"),
                    "horizon": config.get(section, "Horizon"),
                    "project_id": config.get(section, "ProjectID"),
                }
            }
        )

    return providers


def get_settings():
    """Reading profile settings from env"""

    d = {}
    try:
        # d['os_protocol'] = os.environ['OS_PROTOCOL']
        # d['os_identity_api_version'] = os.environ['OS_IDENTITY_API_VERSION']
        # d['os_identity_provider'] = os.environ['OS_IDENTITY_PROVIDER']
        # d['os_auth_type'] = os.environ['OS_AUTH_TYPE']

        d["CHECKIN_CLIENT_ID"] = os.environ["CHECKIN_CLIENT_ID"]
        d["CHECKIN_CLIENT_SECRET"] = os.environ["CHECKIN_CLIENT_SECRET"]
        d["CHECKIN_REFRESH_TOKEN"] = os.environ["CHECKIN_REFRESH_TOKEN"]
        d["CHECKIN_AUTH_URL"] = os.environ["CHECKIN_AUTH_URL"]

        d["PROVIDERS_SETTINGS_FILENAME"] = os.environ["PROVIDERS_SETTINGS_FILENAME"]
        d["MAX_OFFSET"] = os.environ["MAX_OFFSET"]
        d["GOCDB_URL"] = os.environ["GOCDB_URL"]
        d["GOCDB_ENDPOINTS_PATH"] = os.environ["GOCDB_ENDPOINTS_PATH"]
        d["TENANT_NAME"] = os.environ["TENANT_NAME"]

        d["LDAP_SERVER"] = os.environ["LDAP_SERVER"]
        d["LDAP_USERNAME"] = os.environ["LDAP_USERNAME"]
        d["LDAP_PASSWD"] = os.environ["LDAP_PASSWD"]
        d["LDAP_SEARCH_BASE"] = os.environ["LDAP_SEARCH_BASE"]
        d["LDAP_SEARCH_FILTER"] = os.environ["LDAP_SEARCH_FILTER"]

        d["VERBOSE"] = os.environ["VERBOSE"]

    except:
        print(colourise("red", "ERROR: os.environment settings not found!"))

    return d


def pretty_hostname(url):
    """Parsing of the hostname"""

    tmp = url.split("/")
    return tmp[0] + "//" + tmp[2] + "/" + tmp[3]


def check_SSL_certificate(url, verbose):
    """Check SSL certificate expiration date of a server hostname"""

    hostname = urllib.parse.urlparse(url).hostname
    port = urllib.parse.urlparse(url).port

    if verbose == 1:
        print("- Checking SSL certificate in progres...")
    now = datetime.now()
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            if verbose == 1:
                print(json.dumps(ssock.getpeercert()))

            expire_data = json.dumps(ssock.getpeercert()["notAfter"][:-4])

            # Stripping (") from string
            expire_data = expire_data[1:]
            expire_data = expire_data[:-1]

            date_time_obj = datetime.strptime(expire_data, "%b %d %H:%M:%S %Y")

            if date_time_obj > now:
                return "valid"
            else:
                return "expired"


def connect_LDAP(
    LDAP_server,
    LDAP_username,
    LDAP_passwd,
    LDAP_search_base,
    LDAP_search_filter,
    userID,
):
    """Connecting to the EGI LDAP server and fetching users"""

    # Create the server ojbect for onnecting the EGI LDAP server
    server = ldap3.Server(LDAP_server, get_info=ALL)

    # Create a connection object, and bind with the given DN and password.
    conn = ldap3.Connection(server, LDAP_username, password=LDAP_passwd, auto_bind=True)

    # Perform a search for a pre-defined criteria.
    entries = conn.search(LDAP_search_base, LDAP_search_filter, attributes=["*"])

    # Print the resulting entries
    for entry in conn.entries:
        if userID in entry["voPersonID"]:
            # print("\n- User: %s" %entry['cn'])
            # print("- UserID: %s" %entry['voPersonID'])
            # print("- Mail: %s" %entry['mail'])
            # print("- CO groups: %s" %entry['isMemberOf'])
            # print("- Status: %s" %entry['voPersonStatus'])
            return entry["mail"]
