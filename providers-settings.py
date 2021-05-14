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

import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pyGetScopedToken import get_OIDC_Token, get_scoped_Token, get_unscoped_Token
from utils import colourise, highlight, get_settings, pretty_hostname


__author__ = "Giuseppe LA ROCCA"
__email__ = "giuseppe.larocca@egi.eu"
__version__ = "$Revision: 1.0.1"
__date__ = "$Date: 27/04/2021 18:40:27"
__copyright__ = "Copyright (c) 2021 EGI Foundation"
__license__ = "Apache Licence v2.0"

# EGI GOC database settings
# GOC_DB_URL = "goc.egi.eu"
# GOC_DB_PATH = "gocdbpi/public/?method=get_service_endpoint&service_type=org.openstack.nova&monitored=Y"

# Other settings:
# PROVIDERS_SETTINGS_FILENAME = "providers-settings.ini"
# TENANT_NAME = "access"


def get_GOCDB_endpoints(goc_db_url, path):
    """ Retrieve the list of endpoints from the GOC DB """

    url = "https://%s/%s" % (goc_db_url, path)
    curl = requests.get(url=url)

    if curl.status_code == 200:
        root = ET.fromstring(curl.content)

    return root


def get_service_catalogue_details(os_auth_url, unscoped_token):
    """ Get a list of service catalogues """

    url = "%s/auth/catalog" % (os_auth_url)
    headers = {"X-Auth-Token": "%s" % unscoped_token}

    # print(url)
    curl = requests.get(url=url, headers=headers)

    if curl.status_code == 200:
        data = curl.json()["catalog"]

    return data


def get_projects(os_auth_url, unscoped_token):
    """ Get the list of projects enabled in the provider """

    url = "%s/auth/projects" % (os_auth_url)
    headers = {"X-Auth-Token": "%s" % unscoped_token}

    curl = requests.get(url=url, headers=headers)
    if curl.status_code == 200:
        data = curl.json()["projects"]
    else:
        data = ""

    return data


def main():

    print("Configuring providers settings in progress...")
    print("This operation may take time. Please wait!")

    # Get the user's settings
    creds = get_settings()

    # Get endpoints from the EGI GOCDB
    print(colourise("blue", "Fetching the providers endpoints from the EGI GOCDB"))
    endpoints = get_GOCDB_endpoints(creds["GOC_DB_URL"], creds["GOC_DB_PATH"])

    now = datetime.now()
    now_format = now.strftime("%d/%m/%Y %H:%M:%S")

    # Parsing results and save settings
    with open(creds["PROVIDERS_SETTINGS_FILENAME"], "w") as file:

        file.writelines("# Settings of the EGI FedCloud providers\n")
        file.writelines("# Last update: %s\n" % now_format)
        file.writelines("#\n")

        for item in endpoints.findall("SERVICE_ENDPOINT"):
            production = item.find("IN_PRODUCTION").text
            monitored = item.find("NODE_MONITORED").text
            country = item.find("COUNTRY_NAME").text
            rocname = item.find("ROC_NAME").text
            sitename = item.find("SITENAME").text
            hostname = item.find("HOSTNAME").text
            os_auth_url = item.find("URL").text
            gocdb_portal_url = item.find("GOCDB_PORTAL_URL").text

            if "Y" in production and "Y" in monitored:

                # Get the user's credentials
                settings = get_settings()

                # Initialize the OIDC token from the EGI AAI Check-In service.
                token = get_OIDC_Token(
                    settings["checkin_auth_url"],
                    settings["checkin_client_id"],
                    settings["checkin_client_secret"],
                    settings["checkin_refresh_token"],
                )

                try:
                    # Retrieve an "unscoped" token from the provider
                    unscoped_token = get_unscoped_Token(os_auth_url, token)

                    # Get the list of projects enabled in the provider
                    projects = get_projects(os_auth_url, unscoped_token)
                    print(
                        colourise(
                            "green",
                            "- No.%d tenant(s) supported by the resource provider: %s"
                            % (len(projects), sitename),
                        )
                    )

                    for project in projects:
                        # Get the project metadata
                        project_id = project["id"]
                        project_name = project["name"]
                        project_enabled = project["enabled"]
                        print(project_enabled, project_name)

                        if creds["TENANT_NAME"] in project_name:
                            print(
                                colourise(
                                    "yellow",
                                    "- Tenant published by the resource provider.",
                                )
                            )
                            # Retrieve a "scoped" token from the provider
                            scoped_token = get_scoped_Token(
                                os_auth_url, project_id, unscoped_token
                            )
                            # Get the list of catalogue services
                            endpoints = get_service_catalogue_details(
                                os_auth_url, scoped_token
                            )

                            for endpoint in endpoints:
                                endpoint_id = endpoint["id"]
                                endpoint_name = endpoint["name"]
                                urls = endpoint["endpoints"]

                                for url in urls:
                                    endpoint_url = url["url"]
                                    endpoint_interface = url["interface"]
                                    if (
                                        "public" in endpoint_interface
                                        and "nova" in endpoint_name
                                    ):
                                        nova_endpoint = pretty_hostname(endpoint_url)

                            # Saving providers settings
                            file.writelines("\n")
                            file.writelines("[%s]\n" % sitename)
                            file.writelines("ROC_Name: %s\n" % rocname)
                            file.writelines("Name: %s\n" % sitename)
                            file.writelines("Country: %s\n" % country)
                            file.writelines("Identity: %s\n" % os_auth_url)
                            file.writelines("Compute: %s\n" % nova_endpoint)
                            file.writelines("GOC Portal URL: %s\n" % gocdb_portal_url)
                            file.writelines("# %s\n" % project_name)
                            file.writelines("ProjectID: %s\n" % project_id)
                            file.flush()
                except:
                    pass

        file.close()
        print(colourise("green", "Saving providers settings [DONE]"))


if __name__ == "__main__":
    main()
