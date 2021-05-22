# fedcloud-vm-monitoring

This repository contains the Python clients to monitor the EGI FedCloud resources
allocation and removing long-running instances.
The clients work with OpenStack cloud providers supporting the OIDC protocol.

## Requirements

* Basic knowledge of the `json`, `requests`, `configparser` and other basic python
  libraries are requested
* Python v3.5+

## Configure the environment

Edit and export the settings:

<pre>
]$ cat openrc.sh

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
export MAX_OFFSET=720

# EGI GOC database settings 
export GOC_DB_URL="goc.egi.eu"
export GOC_DB_PATH="gocdbpi/public/?method=get_service_endpoint&service_type=org.openstack.nova&monitored=Y"

# The tenant name to be monitored in the cloud providers.
export TENANT_NAME="access"

# Enable verbose logging
# VERBOSE=0, no verbose logging is OFF
# VERBOSE=1, verbose logging is ON
export VERBOSE=1

# Sourcing the env. variables
]$ . openrc.sh
</pre>

## Configure the providers setting

Create a list of cloud providers to be monitored with the
`providers-settings.py` python client.

This list is generated harvesting the indentity endpoints
of the cloud providers in production status from the EGI GOCDB service.

For each cloud provider, the following settings are provided:

<pre>
[PROVIDER HOSTNAME]
ROC_Name: ROC_NAME 
Sitename: PROVIDER SITENAME
Name: PROVIDER HOSTNAME
Country: COUNTRY OF THE PROVIDER [COUNTRY ISO CODE]
Identity: KEYSTONE_URL
Compute: NOVA_URL
GOC Portal URL: ENTRY IN THE EGI GOCDB
ProjectID: PROJECT_ID 
</pre>

## Usage

For simple one-off requests, use this library as a drop-in replacement
for the requests library:

<pre>
]$ python3 providers-settings.py

Configuring providers settings in progress...
This operation may take time. Please wait!
Fetching the providers endpoints from the EGI GOCDB

- Fetching metadata from IFCA-LCG2
- The SSL host certificate of the server is valid

- Get the list of projects *supported* by the provider
- No.7 tenant(s) supported by the resource provider: IFCA-LCG2
True VO:vo.nextgeoss.eu
True VO:acc-comp.egi.eu
False VO:vo.mrilab.es
True VO:openrisknet.eu
True VO:vo.access.egi.eu
True VO:enmr.eu
True VO:training.egi.eu
- Tenant published by the resource provider.

- Fetching metadata from IN2P3-IRES
- The SSL host certificate of the server is valid

- Get the list of projects *supported* by the provider
- No.3 tenant(s) supported by the resource provider: IN2P3-IRES
True EGI_biomed
True EGI_access
True EGI_FCTF

[..]
Saving providers settings [DONE]
</pre>

The settings of the cloud providers supporting the `access` tenant are stored in
the `PROVIDERS_SETTINGS_FILENAME` file:

<pre>
]$ cat providers-settings.ini

# Settings of the EGI FedCloud providers
# Last update: 29/04/2021 16:36:19
#

[IFCA-LCG2]
ROC_Name: NGI_IBERGRID
Sitename: IFCA-LCG2
Country: Spain [ES]
Identity: https://api.cloud.ifca.es:5000/v3/
Compute: https://api.cloud.ifca.es:8774/v2.1
GOC Portal URL: https://goc.egi.eu/portal/index.php?Page_Type=Service&id=7513
# VO:vo.access.egi.eu
ProjectID: 999f045cb1ff4684a15ebb338af69460

[..]
</pre>

## Checking long-running VM instances running in the EGI Federation

<pre>
]$ python3 fedcloud-vm-monitoring.py 

[.] Reading settings of the provider: IFCA-LCG2 
{
    "provider": {
        "hostname": "api.cloud.ifca.es",
        "project_id": "f1d0308880134d04964097524eace710",
        "sitename": "IFCA-LCG2",
        "ROC_name": "NGI_IBERGRID",
        "compute": "https://api.cloud.ifca.es:8774/v2.1",
        "identity": "https://api.cloud.ifca.es:5000/v3/",
        "country": "Spain [ES]"
    }
}

[+] Total VM instance(s) running in the provider = [#1]
_____________________________________________________________
- instance name = EGI_CentOS_8-161470352152 
- instance_id   = https://api.cloud.ifca.es:8774/v2.1/999f045cb1ff4684a15ebb338af69460/servers/966d49a2-81ac-4301-9d92-d68c7dfbc75a 
- status        = ACTIVE 
- ip address    = 193.146.75.230 
- image flavor  = cm4.2xlarge with 8 vCPU cores, 15000 of RAM and 30GB of local disk 
- created at    = 2021-03-02T16:45:28Z 
- elapsed time  = 1389.98 (hours)
  WARNING   = User not authorized to perform the requested action: 'identity:get_user'
- created by    = 5bd063142ec146a1ba93b794eaded9d2 

[-] <b>WARNING: The VM instance elapsed time exceed the max offset!
[-]    Deleting of the instance [966d49a2-81ac-4301-9d92-d68c7dfbc75a] in progress ...
       Do you want to remove the running VM (y/n) ? y</b>
[..]

</pre>

## Links

* https://docs.openstack.org/api-ref/
* https://docs.openstack.org/keystone/pike/api_curl_examples.html
