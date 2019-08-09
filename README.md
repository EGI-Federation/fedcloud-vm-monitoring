# fedcloud-vm-monitoring
This repository contains the Python client to monitor the EGI FedCloud infrastructure resources allocation and removing long-running instances.
The client works with OpenStack cloud providers supporting the OIDC protocol.

## Requirements
* Basic knowledge of the `json`, `os`, `requests`, `datetime` and `ConfigParser` python libraries are requested
* Python v2.7.12+
* Cloud providers enabling the `"identity:get_user": ""` policy

## Settings 
For each cloud provider, the following settings have to be provided:

<pre>
[PROVIDER HOSTNAME]
Name: PROVIDER HOSTNAME
Country: COUNTRY OF THE PROVIDER
Identity: KEYSTONE URL
Compute: NOVA URL
ProjectID: PROJECT_ID 
</pre>

Save these settings in the `providers-settings.ini` configuration file.

## Usage

For simple one-off requests, use this library as a drop-in replacement for the requests library:

<pre>
# This configuration file contains the settings of EFI cloud providers to be checked.
training_settings = "providers-settings.ini"

# These are the EGI AAI Check-In settings used to generate a valid access token
# DO NOT CHANGE THE SETTINGS BELOW!
client_id = "f33e824a-078d-497b-b700-25b0df7fc5b7"
client_secret = "B80vPK0LVbYuvwRj0Aexs8y0rKgk5XHwYRRq3BCr33ejj33385bzDVcPmSTUkqA2QjMiwWKJDTxvOou7yVV8EA"
refresh_token = "eyJhbGciOiJub25lIn0.eyJleHAiOjE1ODQyNzQxNDYsImp0aSI6IjkzNGMxNTBhLTA4NDQtNDI5ZC05NDJhLTIwMzIxMDgzNzIzMSJ9."
checkin_auth_url = "https://aai.egi.eu/oidc/token"

# Set the max elapsed time (in hours) for a running instance in the EGI FedCloud infrastructure
# Considering as offset 1 mounth = 30 days * 24h = 720 hours
offset = 720 # Change here!
</pre>

## Listing long-running instances

<pre>
]$ python fedcloud-vm-monitoring.py 

[.] Reading the configuration settings of the cloud provider: CESNET-MCC 

{
    "provider": {
        "country": "Czech Republic", 
        "project_id": "eae2aa7f26334104906106bca4b82ae3", 
        "compute": "https://compute.cloud.muni.cz/v2.1", 
        "name": "CESNET-MCC", 
        "identity": "https://identity.cloud.muni.cz/v3"
    }
}

[+] Get running instance(s) [#5] from the provider ...
WARNING: User not authorized to perform the requested action: 'identity:get_user'

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = k8s-fat-2 
[-] instance_id   = http://compute.cloud.muni.cz/v2.1/eae2aa7f26334104906106bca4b82ae3/servers/5b239153-ded7-4db9-8283-02bb1ead5935 
[-] status        = ACTIVE 
[-] ip address    = 192.168.13.37 
[-] image flavor  = standard.xxlarge with 8 vCPU cores, 32768 of RAM and 80GB of local disk 
[-] created at    = 2019-07-31T09:05:08Z 
[-] created by    = 05228772e737467bbd5f5138d362d6a2 
[-] elapsed time  = 218.47 (hours)
WARNING: User not authorized to perform the requested action: 'identity:get_user'

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = k8s-fat-1 
[-] instance_id   = http://compute.cloud.muni.cz/v2.1/eae2aa7f26334104906106bca4b82ae3/servers/6f7aef51-2823-4b1e-9d80-fcde1b60964a 
[-] status        = ACTIVE 
[-] ip address    = 192.168.13.44 
[-] image flavor  = standard.xxlarge with 8 vCPU cores, 32768 of RAM and 80GB of local disk 
[-] created at    = 2019-07-31T08:23:54Z 
[-] created by    = 05228772e737467bbd5f5138d362d6a2 
[-] elapsed time  = 219.16 (hours)
WARNING: User not authorized to perform the requested action: 'identity:get_user'

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = k8s-fat-0 
[-] instance_id   = http://compute.cloud.muni.cz/v2.1/eae2aa7f26334104906106bca4b82ae3/servers/9cf4b36c-0abb-483f-9e02-fadd38e87f8c 
[-] status        = ACTIVE 
[-] ip address    = 78.128.251.190 
[-] image flavor  = standard.xxlarge with 8 vCPU cores, 32768 of RAM and 80GB of local disk 
[-] created at    = 2019-07-31T07:17:58Z 
[-] created by    = 05228772e737467bbd5f5138d362d6a2 
[-] elapsed time  = 220.26 (hours)
WARNING: User not authorized to perform the requested action: 'identity:get_user'

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = k8s-master 
[-] instance_id   = http://compute.cloud.muni.cz/v2.1/eae2aa7f26334104906106bca4b82ae3/servers/cf125cc2-22a3-4a94-9989-876ab32a5354 
[-] status        = ACTIVE 
[-] ip address    = 192.168.13.58 
[-] image flavor  = standard.medium with 2 vCPU cores, 4096 of RAM and 80GB of local disk 
[-] created at    = 2019-07-12T06:20:47Z 
[-] created by    = 05228772e737467bbd5f5138d362d6a2 
[-] elapsed time  = 677.21 (hours)
WARNING: User not authorized to perform the requested action: 'identity:get_user'

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = k8s-workers-1 
[-] instance_id   = http://compute.cloud.muni.cz/v2.1/eae2aa7f26334104906106bca4b82ae3/servers/4c807302-1d74-49cb-849a-f7559d126133 
[-] status        = ACTIVE 
[-] ip address    = 78.128.251.232 
[-] image flavor  = standard.large with 4 vCPU cores, 8192 of RAM and 80GB of local disk 
[-] created at    = 2019-07-08T12:28:37Z 
[-] created by    = 05228772e737467bbd5f5138d362d6a2 
[-] elapsed time  = 767.08 (hours)

<b>WARNING: The instance elapsed time exceed the max offset!</b>
[-] Deleting of the instance [4c807302-1d74-49cb-849a-f7559d126133] in progress ...
Do you want to remove the running VM (y/n) ? n
Aborting ...

[.] Reading the configuration settings of the cloud provider: IFCA-LCG2 

{
    "provider": {
        "country": "Spain", 
        "project_id": "f1d0308880134d04964097524eace710", 
        "compute": "https://api.cloud.ifca.es:8774/v2.1", 
        "name": "IFCA-LCG2", 
        "identity": "https://api.cloud.ifca.es:5000/v3"
    }
}

[+] Get running instance(s) [#1] from the provider ...
WARNING: User not authorized to perform the requested action: 'identity:get_user'

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = onedata 
[-] instance_id   = https://api.cloud.ifca.es:8774/v2.1/f1d0308880134d04964097524eace710/servers/d44c38d9-d8f8-43fc-9f05-ccf31e004171 
[-] status        = ACTIVE 
[-] ip address    = 193.146.75.141 
[-] image flavor  = cm4.2xlarge with 8 vCPU cores, 15000 of RAM and 30GB of local disk 
[-] created at    = 2019-08-01T14:03:57Z 
[-] created by    = 15bbc31fbe034adf9dbb2c1d8ebe0e05 
[-] elapsed time  = 189.50 (hours)

[.] Reading the configuration settings of the cloud provider: INFN-CATANIA-STACK 

{
    "provider": {
        "country": "Italy", 
        "project_id": "00982464978c4b61a5f570e315251f02", 
        "compute": "http://stack-server.ct.infn.it:8774/v2.1", 
        "name": "INFN-CATANIA-STACK", 
        "identity": "https://stack-server.ct.infn.it:5000/v3"
    }
}

[+] Get running instance(s) [#7] from the provider ...

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = im_userimage 
[-] instance_id   = http://stack-server.ct.infn.it:8774/v2.1/00982464978c4b61a5f570e315251f02/servers/7f6891ac-f695-443d-8bed-90dcc6592952 
[-] status        = ACTIVE 
[-] ip address    = 212.189.145.37 
[-] image flavor  = m1.medium with 2 vCPU cores, 4096 of RAM and 40GB of local disk 
[-] created at    = 2019-07-31T17:10:53Z 
[-] created by    = /C=IT/O=INFN/OU=Personal Certificate/L=Catania/CN=Giuseppe La Rocca 
[-] elapsed time  = 210.38 (hours)

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = im_userimage 
[-] instance_id   = http://stack-server.ct.infn.it:8774/v2.1/00982464978c4b61a5f570e315251f02/servers/4b2ac454-cfa9-4734-9cd0-7a12cd1c24b6 
[-] status        = ACTIVE 
[-] ip address    = 212.189.145.34 
[-] image flavor  = m1.medium with 2 vCPU cores, 4096 of RAM and 40GB of local disk 
[-] created at    = 2019-07-31T17:10:22Z 
[-] created by    = /C=IT/O=INFN/OU=Personal Certificate/L=Catania/CN=Giuseppe La Rocca 
[-] elapsed time  = 210.40 (hours)

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = im_userimage 
[-] instance_id   = http://stack-server.ct.infn.it:8774/v2.1/00982464978c4b61a5f570e315251f02/servers/723e4c9b-4bf0-4fa0-a976-dc76f01938e2 
[-] status        = ACTIVE 
[-] ip address    = 212.189.145.31 
[-] image flavor  = m1.medium with 2 vCPU cores, 4096 of RAM and 40GB of local disk 
[-] created at    = 2019-07-31T17:10:10Z 
[-] created by    = /C=IT/O=INFN/OU=Personal Certificate/L=Catania/CN=Giuseppe La Rocca 
[-] elapsed time  = 210.40 (hours)

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = im_userimage 
[-] instance_id   = http://stack-server.ct.infn.it:8774/v2.1/00982464978c4b61a5f570e315251f02/servers/2a0cddf2-b06b-4d1a-837d-2106602740e6 
[-] status        = ACTIVE 
[-] ip address    = 212.189.145.30 
[-] image flavor  = m1.medium with 2 vCPU cores, 4096 of RAM and 40GB of local disk 
[-] created at    = 2019-07-31T17:10:02Z 
[-] created by    = /C=IT/O=INFN/OU=Personal Certificate/L=Catania/CN=Giuseppe La Rocca 
[-] elapsed time  = 210.41 (hours)

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = im_userimage 
[-] instance_id   = http://stack-server.ct.infn.it:8774/v2.1/00982464978c4b61a5f570e315251f02/servers/dc76df85-e459-4c3d-ab20-b502c86d008a 
[-] status        = ACTIVE 
[-] ip address    = 212.189.145.176 
[-] image flavor  = m1.medium with 2 vCPU cores, 4096 of RAM and 40GB of local disk 
[-] created at    = 2019-07-31T17:09:54Z 
[-] created by    = /C=IT/O=INFN/OU=Personal Certificate/L=Catania/CN=Giuseppe La Rocca 
[-] elapsed time  = 210.42 (hours)

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = im_userimage 
[-] instance_id   = http://stack-server.ct.infn.it:8774/v2.1/00982464978c4b61a5f570e315251f02/servers/d050e570-8d69-4387-bc5b-4feee754fc1f 
[-] status        = ACTIVE 
[-] ip address    = 212.189.145.169 
[-] image flavor  = m1.medium with 2 vCPU cores, 4096 of RAM and 40GB of local disk 
[-] created at    = 2019-07-31T16:53:39Z 
[-] created by    = /C=IT/O=INFN/OU=Personal Certificate/L=Catania/CN=Giuseppe La Rocca 
[-] elapsed time  = 210.69 (hours)

[ Reporting ] _____________________________________________________________________________________________________________________
[-] instance name = EGI_FedCloudClient 
[-] instance_id   = http://stack-server.ct.infn.it:8774/v2.1/00982464978c4b61a5f570e315251f02/servers/93211ce7-1dd0-4b71-8ce4-780e5f97ce0c 
[-] status        = ACTIVE 
[-] ip address    = 212.189.145.36 
[-] image flavor  = m1.large with 4 vCPU cores, 8192 of RAM and 80GB of local disk 
[-] created at    = 2018-02-12T08:56:38Z 
[-] created by    = egi 
[-] elapsed time  = 13034.64 (hours)

<b>WARNING: The instance elapsed time exceed the max offset!</b>
[-] Deleting of the instance [93211ce7-1dd0-4b71-8ce4-780e5f97ce0c] in progress ...
Do you want to remove the running VM (y/n) ? n
Aborting ...

</pre>


# Template for EGI repositories.

It includes:

* License information
* Copyright and author information
* Code of conduct and contribution guidelines
* Templates for PR and issues

Content is based on:

* [Contributor Covenant](http://contributor-covenant.org)
* [Semantic Versioning](https://semver.org/)
* [Chef Cookbook Contributing Guide](https://github.com/chef-cookbooks/community_cookbook_documentation/blob/master/CONTRIBUTING.MD)
