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
