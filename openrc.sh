#!/bin/bash

# General settings
export OS_PROTOCOL="openid"
export OS_IDENTITY_API_VERSION=3
export OS_IDENTITY_PROVIDER="egi.eu"
export OS_AUTH_TYPE="v3oidcaccesstoken"

# EGI AAI Check-In settings
export CHECKIN_CLIENT_ID="..."
export CHECKIN_CLIENT_SECRET="..."
export CHECKIN_REFRESH_TOKEN="..."
export CHECKIN_AUTH_URL="https://aai.egi.eu/oidc/token"

# This configuration file contains the settings of EGI cloud providers to be checked.
export PROVIDERS_SETTINGS_FILENAME="providers-settings.ini"

# Set the max elapsed time (in hours) for a running instance in the EGI FedCloud infrastructure
# E.g.: 1 mounth = 30 days * 24h = 720 hours
# If MAX_OFFSET=-1, all the running VMs in the tenant of the providers will be deleted
export MAX_OFFSET=-1

# EGI GOC database settings 
export GOC_DB_URL="goc.egi.eu"
export GOC_DB_PATH="gocdbpi/public/?method=get_service_endpoint&service_type=org.openstack.nova&monitored=Y"

# Other settings
export TENANT_NAME="access"
