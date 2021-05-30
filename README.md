# fedcloud-vm-monitoring

This repository contains the Python clients to monitor the EGI FedCloud resources
allocation and removing long-running instances.
The clients work with OpenStack cloud providers supporting the OIDC protocol.

## Requirements

* Basic knowledge of the `json`, `requests`, `configparser` and other basic python
  libraries are requested
* Basic knowledge of virtualenv
* Python v3.9+

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

Use virtualenv to configure the working:

<pre>
]$ virtualenv -p /usr/bin/python3.9 venv
Running virtualenv with interpreter /usr/bin/python3.9
Using base prefix '/usr'
/usr/local/lib/python2.7/dist-packages/virtualenv.py:1047: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
  import imp
New python executable in /home/larocca/APIs/fedcloud-vm-monitoring/venv/bin/python3.9
Also creating executable in /home/larocca/APIs/fedcloud-vm-monitoring/venv/bin/python
Installing setuptools, pip, wheel...done.

]$ source venv/bin/activate
</pre>

Install the missing libraries with pip:

<pre>
]$ python3 -m pip install requests pytz
[..]
</pre>

## Configure settings

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

[+] Total VM instance(s) running in the provider = [#3]
_____________________________________________________________
- instance name = test 
- instance_id   = https://api.cloud.ifca.es:8774/v2.1/999f045cb1ff4684a15ebb338af69460/servers/044959ce-a3f8-4fe9-bd6f-31b6cc3f6b27 
- status        = ACTIVE 
- ip address    = 172.16.8.3 
- image flavor  = m1.small with 1 vCPU cores, 2000 of RAM and 10GB of local disk 
- created at    = 2021-05-24T09:03:28Z 
- elapsed time  = 0.49 (hours)
- created by    = 025166931789a0f57793a6092726c2ad89387a4cc167e7c63c5d85fc91021d18@egi.eu 

[-] WARNING: The VM instance elapsed time exceed the max offset!
[-] Deleting of the instance [044959ce-a3f8-4fe9-bd6f-31b6cc3f6b27] in progress ...
Do you want to remove the running VM (y/n) ? y
[DONE] Server instance successfully removed from the provider.
_____________________________________________________________
- instance name = EGI_Ubuntu_20_04-162099572521 
- instance_id   = https://api.cloud.ifca.es:8774/v2.1/999f045cb1ff4684a15ebb338af69460/servers/328e3845-93c0-4d57-bd10-11acfd9c5ee7 
- status        = ACTIVE 
- ip address    = 172.16.8.13 
- image flavor  = cm4.2xlarge with 8 vCPU cores, 15000 of RAM and 30GB of local disk 
- created at    = 2021-05-14T12:35:27Z 
- elapsed time  = 236.97 (hours)
  WARNING   = User not authorized to perform the requested action: 'identity:get_user'
- created by    = aba1ce2db1694003879ac987e08c87b1 

[-] WARNING: The VM instance elapsed time exceed the max offset!
[-] Deleting of the instance [328e3845-93c0-4d57-bd10-11acfd9c5ee7] in progress ...
Do you want to remove the running VM (y/n) ? n
[..]
</pre>

## Links

* https://docs.openstack.org/api-ref/
* https://docs.openstack.org/keystone/pike/api_curl_examples.html
