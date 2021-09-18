# fedcloud-vm-monitoring

This repository contains the Python clients to monitor the EGI FedCloud resources
allocation and removing long-running instances.
The clients work with OpenStack cloud providers supporting the OIDC protocol.

## Requirements

* Basic knowledge of the `json`, `requests`, `configparser`, `ldap3` and other basic python
  libraries is requested
* Basic knowledge of `virtualenv` is requested
* Python v3.9+
* Cloud providers enabling the `"identity:get_user": ""` policy

## Installation

Make sure that your environment has the EGI CAs properly installed and
configured for python:

If you don’t have the CA certificates installed in your machine, you can get
them from the [UMD EGI core Trust Anchor Distribution](http://repository.egi.eu/?category_name=cas)

Once installed, get the location of the requests CA bundle with:

```
python3 -m requests.certs
```

If the output of that command is `/etc/ssl/certs/ca-certificates.crt`, you can
add EGI CAs by executing:

```
cd /usr/local/share/ca-certificates
for f in /etc/grid-security/certificates/*.pem ; do ln -s $f $(basename $f .pem).crt; done
update-ca-certificates
```

If the output is `/etc/pki/tls/certs/ca-bundle.crt` add the EGI CAs with:

```
cd /etc/pki/ca-trust/source/anchors
ln -s /etc/grid-security/certificates/*.pem .
update-ca-trust extract
```

Otherwise, you are using internal requests bundle, which can be augmented with
the EGI CAs with:

```
cat /etc/grid-security/certificates/*.pem >> $(python -m requests.certs)
```

## Configuring the environment

Use virtualenv to configure the working environment:

```
]$ virtualenv -p /usr/bin/python3.9 venv
Running virtualenv with interpreter /usr/bin/python3.9
Using base prefix '/usr'
/usr/local/lib/python2.7/dist-packages/virtualenv.py:1047: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
  import imp
New python executable in /home/larocca/APIs/fedcloud-vm-monitoring/venv/bin/python3.9
Also creating executable in /home/larocca/APIs/fedcloud-vm-monitoring/venv/bin/python
Installing setuptools, pip, wheel...done.

]$ source venv/bin/activate
```

Install the libraries `requests`, `pytz` and `ldap3` with pip:

```
]$ python3 -m pip install requests pytz ldap3
[..]
```

## Configure settings

Edit and export the settings:

```
]$ cat openrc.sh

#!/bin/bash

# EGI AAI Check-In settings
export CHECKIN_CLIENT_ID="..."
export CHECKIN_CLIENT_SECRET="..."
export CHECKIN_REFRESH_TOKEN="..."
export CHECKIN_AUTH_URL="https://aai.egi.eu/oidc/token"

# EGI GOC_DB database settings
export GOC_DB_URL="goc.egi.eu"
export GOC_DB_PATH="gocdbpi/public/?method=get_service_endpoint&service_type=org.openstack.nova&monitored=Y"

# EGI LDAP server settings
export LDAP_SERVER="ldaps://ldap.aai-dev.egi.eu"
export LDAP_PASSWD="..."
xport LDAP_USERNAME="cn=vo_access_admin,dc=ldap,dc=aai-dev,dc=egi,dc=eu"
export LDAP_SEARCH_BASE="ou=people,dc=ldap,dc=aai-dev,dc=egi,dc=eu"
export LDAP_SEARCH_FILTER="(isMemberOf=CO:COU:vo.access.egi.eu:members)"

# This configuration file contains the settings of EGI cloud providers to be checked.
export PROVIDERS_SETTINGS_FILENAME="providers-settings.ini"

# Set the max elapsed time (in hours) for a running instance in the EGI FedCloud infrastructure
# E.g.: 1 mounth = 30 days * 24h = 720 hours
# If MAX_OFFSET=-1, all the running VMs in the tenant of the providers will be deleted
export MAX_OFFSET=720

# The tenant name to be monitored in the cloud providers.
export TENANT_NAME="access"

# Enable verbose logging
# VERBOSE=INFO, no verbose logging is OFF
# VERBOSE=DEBUG, verbose logging is ON
export VERBOSE=DEBUG

# Sourcing the env. variables
]$ . openrc.sh
```

## Configure the providers setting

Create a list of cloud providers to be monitored with the
`providers-settings.py` python client.

This list is generated harvesting the indentity endpoints
of the cloud providers in production status from the EGI GOCDB service.

For each cloud provider, the following settings are provided:

```
[PROVIDER HOSTNAME]
ROC_Name: ROC_NAME
Sitename: PROVIDER SITENAME
Hostname: PROVIDER HOSTNAME
Country: COUNTRY OF THE PROVIDER [COUNTRY ISO CODE]
Identity: KEYSTONE_URL
Compute: NOVA_URL
GOC Portal URL: ENTRY IN THE EGI GOCDB
ProjectID: PROJECT_ID
```

## Usage

For simple one-off requests, use this library as a drop-in replacement
for the requests library:

```
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
```

The settings of the cloud providers supporting the `access` tenant are stored in
the `PROVIDERS_SETTINGS_FILENAME` file:

```
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
```

## Checking long-running VM instances in the EGI Federated Cloud

```
]$ python3 fedcloud-vm-monitoring.py
Verbose Level = DEBUG
Max elapsed time = 4320 (in hours) for a running instance in EGI

[.] Reading settings of the provider: api.cloud.ifca.es
{
    "provider": {
        "sitename": "IFCA-LCG2",
        "identity": "https://api.cloud.ifca.es:5000/v3/",
        "hostname": "api.cloud.ifca.es",
        "ROC_name": "NGI_IBERGRID",
        "country": "Spain [ES]",
        "compute": "https://api.cloud.ifca.es:8774/v2.1",
        "project_id": "999f045cb1ff4684a15ebb338af69460"
    }
}

[+] Total VM instance(s) running in the provider = [#1]
_________________________________________________________________________________
- instance name = EGI_CentOS_8-161470352152 [#1]
- instance_id   = 966d49a2-81ac-4301-9d92-d68c7dfbc75a
- instance_href = https://api.cloud.ifca.es:8774/v2.1/servers/966d49a2-81ac-4301-9d92-d68c7dfbc75a
- status        = ACTIVE
- ip address    = 193.146.75.230
- image flavor  = cm4.2xlarge with 8 vCPU cores, 15000 of RAM and 30GB of local disk
- created at    = 2021-03-02T16:45:28Z
- elapsed time  = 116.71 (days), 3501.29 (hours)
  WARNING       = User not authorized to perform the requested action: 'identity:get_user'
- created by    = 5bd063142ec146a1ba93b794eaded9d2

[-] WARNING: The VM instance elapsed time exceed the max offset!
[-] Deleting of the instance [966d49a2-81ac-4301-9d92-d68c7dfbc75a] in progress ...
Do you want to remove the running VM (y/n) ? y
[DONE] Server instance successfully removed from the provider.

[.] Reading settings of the resource provider: egiosc.gsi.de
{
    "provider": {
        "compute": "http://egiosc.gsi.de:8774/v2.1",
        "country": "Germany [DE]",
        "hostname": "egiosc.gsi.de",
        "identity": "https://egiosc.gsi.de:5000/v3",
        "sitename": "GSI-LCG2",
        "ROC_name": "NGI_DE",
        "project_id": "1392719e6e4c4bf7ba0fce8c0acbbd22"
    }
}
- No VMs instances found in the resource provider

[..]

[.] Reading settings of the resource provider: bulut.truba.gov.tr
{
    "provider": {
        "compute": "http://bulut.truba.gov.tr:8774/v2.1",
        "country": "Turkey [TR]",
        "hostname": "bulut.truba.gov.tr",
        "identity": "https://bulut.truba.gov.tr:5000/v3",
        "sitename": "TR-FC1-ULAKBIM",
        "ROC_name": "NGI_TR",
        "project_id": "2fa316a05d364de9b5a55ac78a45f8bf"
    }
}

[+] Total VM instance(s) running in the resource provider = [#1]
_________________________________________________________________________________
- instance name = test [#1]
- instance_id   = c2c2e450-50d7-4feb-9848-72ec99c3a17b
- instance_href = http://bulut.truba.gov.tr:8774/v2.1/servers/c2c2e450-50d7-4feb-9848-72ec99c3a17b
- status        = SHUTOFF
- ip address    = 172.17.4.207
- image flavor  = m1.medium with 2 vCPU cores, 2048 of RAM and 40GB of local disk
- created at    = 2021-04-28T10:07:14Z
- elapsed time  = 71.34 (days), 2140.34 (hours)
- created by    = 025166931789a0f57793a6092726c2ad89387a4cc167e7c63c5d85fc91021d18@egi.eu
- email         = giuseppe.larocca@egi.eu
```

## Useful links

* https://docs.openstack.org/api-ref/
* https://docs.openstack.org/keystone/pike/api_curl_examples.html
