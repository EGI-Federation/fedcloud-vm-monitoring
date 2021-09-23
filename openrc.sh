#!/bin/bash

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

# EGI GOCDB settings 
# https://goc.egi.eu/gocdbpi/public/?method=get_service_endpoint&service_type=org.openstack.nova&monitored=Y
# https://goc.egi.eu/gocdbpi/public/?method=get_service_endpoint&service_type=org.openstack.horizon&monitored=Y
export GOCDB_URL="goc.egi.eu"
export GOCDB_ENDPOINTS_PATH="gocdbpi/public/?method=get_service_endpoint&service_type="

# EGI LDAP server settings
export LDAP_SERVER="ldaps://ldap.aai-dev.egi.eu"
export LDAP_PASSWD="...." # vo.access.egi.eu
export LDAP_USERNAME="cn=vo_access_admin,dc=ldap,dc=aai-dev,dc=egi,dc=eu"
export LDAP_SEARCH_BASE="ou=people,dc=ldap,dc=aai-dev,dc=egi,dc=eu"
export LDAP_SEARCH_FILTER="(isMemberOf=CO:COU:vo.access.egi.eu:members)"

# Other settings
export TENANT_NAME="access"

# Enable verbose logging
# VERBOSE=INFO, no verbose logging is OFF
# VERBOSE=DEBUG, verbose logging is ON
export VERBOSE=DEBUG

