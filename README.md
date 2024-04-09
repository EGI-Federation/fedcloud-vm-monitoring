# fedcloud-vm-monitoring

This repository contains a Python tool to monitor usage of EGI FedCloud
providers and remove long-running instances. The clients work with OpenStack
cloud providers supporting the OIDC protocol.

## Requirements

- Python v3.9+
- A Check-in account member of the VOs to be monitored
- For getting the EGI user identity, cloud providers have to enable the
  `"identity:get_user"` API call for the user (see
  [VO auditing](https://docs.egi.eu/providers/cloud-compute/openstack/aai/#vo-auditing)
  for more information

## Installation

You can install with `pip` (it is recommended to install in a virtualenv!):

```shell
pip install -U git+https://github.com/EGI-Federation/fedcloud-vm-monitoring.git
```

Some sites use certificates issued by certificate authorities that are not
included in the default OS distribution, if you find SSL errors, please
[install the EGI Core Trust Anchors certificates](https://fedcloudclient.fedcloud.eu/install.html#installing-egi-core-trust-anchor-certificates)

## Running the monitor

For running the tool, you just need a
[valid Check-in token](https://docs.egi.eu/users/aai/check-in/obtaining-tokens/):

```shell
fedcloud-vo-monitor --token <your token>
```

You can tune the behavior with the following parameters:

- `--site SITE_NAME`: restrict the monitoring to the site provided, otherwise
  will check all sites available in GOCDB.
- `--vo VO_NAME`: VO name to monitor, default is `vo.access.egi.eu`.
- `--delete`: if set, ask for deletion of VMs if they go beyond `max-days`
- `--max-days INTEGER`: maximum number of days instances can be running before
  triggering deletion (default 90 days).
- `--show-quotas BOOLEAN`: whether to show quotas for the VO or not (default:
  `True`)

If you have access to
[Check-in LDAP](https://docs.egi.eu/users/aai/check-in/vos/#ldap) for VO
membership, you can specify the settings with the following options:

- `--ldap-user USERNAME`
- `--ldap-password PASSWORD`

The `ldap-server`, `ldap-base-dn` and `ldap-search-filter`, can further tune the
usage of LDAP, but should work for most cases without changes.

### Sample output

```shell
$ fedcloud-vo-monitor --token $ACCESS_TOKEN --vo cloud.egi.eu
[.] Checking VO cloud.egi.eu at 100IT
[-] WARNING: VO cloud.egi.eu is not available at 100IT in AppDB
[-] WARNING: VO cloud.egi.eu is not available at 100IT in fedcloudclient
[.] Checking VO cloud.egi.eu at BIFI
[-] WARNING: VO cloud.egi.eu is not available at BIFI in AppDB
[-] WARNING: VO cloud.egi.eu is not available at BIFI in fedcloudclient
[.] Checking VO cloud.egi.eu at CENI
[-] WARNING: VO cloud.egi.eu is not available at CENI in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CENI in fedcloudclient
[.] Checking VO cloud.egi.eu at CESGA
[-] WARNING: VO cloud.egi.eu is not available at CESGA in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CESGA in fedcloudclient
[.] Checking VO cloud.egi.eu at CESGA-CLOUD
[-] WARNING: VO cloud.egi.eu is not available at CESGA-CLOUD in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CESGA-CLOUD in fedcloudclient
[.] Checking VO cloud.egi.eu at CESNET-MCC
[-] WARNING: VO cloud.egi.eu is not available at CESNET-MCC in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CESNET-MCC in fedcloudclient
[.] Checking VO cloud.egi.eu at CETA-GRID
[-] WARNING: VO cloud.egi.eu is not available at CETA-GRID in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CETA-GRID in fedcloudclient
[.] Checking VO cloud.egi.eu at CLOUDIFIN
[-] WARNING: VO cloud.egi.eu is not available at CLOUDIFIN in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CLOUDIFIN in fedcloudclient
[.] Checking VO cloud.egi.eu at CSTCLOUD-EGI
[-] WARNING: VO cloud.egi.eu is not available at CSTCLOUD-EGI in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CSTCLOUD-EGI in fedcloudclient
[.] Checking VO cloud.egi.eu at CYFRONET-CLOUD
[-] WARNING: VO cloud.egi.eu is not available at CYFRONET-CLOUD in AppDB
[-] WARNING: VO cloud.egi.eu is not available at CYFRONET-CLOUD in fedcloudclient
[.] Checking VO cloud.egi.eu at DESY-CC
[-] WARNING: VO cloud.egi.eu is not available at DESY-CC in AppDB
[-] WARNING: VO cloud.egi.eu is not available at DESY-CC in fedcloudclient
[.] Checking VO cloud.egi.eu at GRNET-OPENSTACK
[-] WARNING: VO cloud.egi.eu is not available at GRNET-OPENSTACK in AppDB
[-] WARNING: VO cloud.egi.eu is not available at GRNET-OPENSTACK in fedcloudclient
[.] Checking VO cloud.egi.eu at GSI-LCG2
[-] WARNING: VO cloud.egi.eu is not available at GSI-LCG2 in AppDB
[-] WARNING: VO cloud.egi.eu is not available at GSI-LCG2 in fedcloudclient
[.] Checking VO cloud.egi.eu at IFCA-LCG2
[-] WARNING: VO cloud.egi.eu is not available at IFCA-LCG2 in AppDB
[-] WARNING: VO cloud.egi.eu is not available at IFCA-LCG2 in fedcloudclient
[.] Checking VO cloud.egi.eu at IISAS-FedCloud
[+] Total VM instance(s) running in the resource provider = 2
Getting VMs information  [####################################]  100%
[+] VM #0  --------------------------------------------------
    instance name  = cloud-info-backup
    instance id    = d4e00df3-cbf7-421e-bf9c-66470bb19441
    status         = ACTIVE
    ip address     = 192.168.10.170
    flavor         = m1.large with 4 vCPU cores, 8192 of RAM and 30 GB of local disk
    created at     = 2024-02-28T08:45:15Z
    elapsed time   = 40 days, 3:14:07.603224
    user           = [REDACTED]
    egi user       = [REDACTED]
    email          = [REDACTED]
[+] VM #1  --------------------------------------------------
    instance name  = dashboard
    instance id    = 8ef9fcce-19e4-41c6-ab03-d1730a924510
    status         = ACTIVE
    ip address     = 192.168.10.69 xxx.xxx.xx.xxx
    flavor         = m1.medium with 2 vCPU cores, 4096 of RAM and 20 GB of local disk
    created at     = 2021-12-02T14:53:32Z
    elapsed time   = 857 days, 21:05:50.603224
    user           = [REDACTED]
    egi user       = [REDACTED]
    email          = [REDACTED]
[-] WARNING The VM instance elapsed time exceed the max offset!
[+] Quota information:
    cores          = 20
    instances      = 10
    ram            = 51200
    floating-ips   = 10
    secgroup-rules = 100
[-] WARNING: Less than 3 security groups per instance
[.] Checking VO cloud.egi.eu at ILIFU-UCT
[-] WARNING: VO cloud.egi.eu is not available at ILIFU-UCT in AppDB
[-] WARNING: VO cloud.egi.eu is not available at ILIFU-UCT in fedcloudclient
[.] Checking VO cloud.egi.eu at IN2P3-IRES
[-] WARNING: VO cloud.egi.eu is not available at IN2P3-IRES in AppDB
[-] WARNING: VO cloud.egi.eu is not available at IN2P3-IRES in fedcloudclient
[.] Checking VO cloud.egi.eu at INFN-CLOUD-BARI
[-] WARNING: VO cloud.egi.eu is not available at INFN-CLOUD-BARI in AppDB
[-] WARNING: VO cloud.egi.eu is not available at INFN-CLOUD-BARI in fedcloudclient
[.] Checking VO cloud.egi.eu at INFN-CLOUD-CNAF
[-] WARNING: VO cloud.egi.eu is not available at INFN-CLOUD-CNAF in AppDB
[-] WARNING: VO cloud.egi.eu is not available at INFN-CLOUD-CNAF in fedcloudclient
[.] Checking VO cloud.egi.eu at NCG-INGRID-PT
[-] WARNING: VO cloud.egi.eu is not available at NCG-INGRID-PT in AppDB
[+] Total VM instance(s) running in the resource provider = 4
Getting VMs information  [------------------------------------]    0%WARNING: Unable to get user list: The request you have made requires authentication. (HTTP 401) (Request-ID: req-5ac539f1-7869-4fd8-9483-8b9eb704d725)

Getting VMs information  [####################################]  100%
[+] VM #0  --------------------------------------------------
    instance name  = test
    instance id    = d2431967-a519-47e4-8d8c-209727840233
    status         = ACTIVE
    ip address     = 192.168.1.233
    flavor         = svc1.m with 2 vCPU cores, 4096 of RAM and 40 GB of local disk
    created at     = 2024-02-29T09:43:01Z
    elapsed time   = 39 days, 2:17:01.266584
    user           = [REDACTED]
[+] VM #1  --------------------------------------------------
    instance name  = cloud-info
    instance id    = 9f8c17b4-5503-42ac-af3d-6ed0c9dea9c7
    status         = ACTIVE
    ip address     = 192.168.1.3
    flavor         = svc1.m with 2 vCPU cores, 4096 of RAM and 40 GB of local disk
    created at     = 2024-02-28T14:39:08Z
    elapsed time   = 39 days, 21:20:54.266584
    user           = [REDACTED]
[+] VM #2  --------------------------------------------------
    instance name  = atrope
    instance id    = d6815b91-599d-4c6a-8d55-a38243148838
    status         = ACTIVE
    ip address     = 192.168.1.250 xxx.xxx.xxx.xxx
    flavor         = svc2.l with 8 vCPU cores, 8192 of RAM and 40 GB of local disk
    created at     = 2022-08-31T07:17:18Z
    elapsed time   = 586 days, 4:42:44.266584
    user           = [REDACTED]
[-] WARNING The VM instance elapsed time exceed the max offset!
[+] VM #3  --------------------------------------------------
    instance name  = nsupdate
    instance id    = 045ec1e7-b47a-4f18-9c9f-06cb30803955
    status         = ACTIVE
    ip address     = 192.168.1.71 xxx.xxx.xxx.xxx
    flavor         = svc2.m with 4 vCPU cores, 4096 of RAM and 40 GB of local disk
    created at     = 2020-11-13T09:01:32Z
    elapsed time   = 1242 days, 2:58:30.266584
    user           = [REDACTED]
[-] WARNING The VM instance elapsed time exceed the max offset!
[+] Quota information:
    ram            = 65536
    instances      = 10
    cores          = 24
    floating-ips   = 2
    secgroup-rules = 100
[-] WARNING: Less than 3 security groups per instance
[-] WARNING: Less than 1 floating IPs per instance
[.] Checking VO cloud.egi.eu at SCAI
[-] WARNING: VO cloud.egi.eu is not available at SCAI in AppDB
[-] WARNING: VO cloud.egi.eu is not available at SCAI in fedcloudclient
[.] Checking VO cloud.egi.eu at TR-FC1-ULAKBIM
[-] WARNING: VO cloud.egi.eu is not available at TR-FC1-ULAKBIM in AppDB
[-] WARNING: VO cloud.egi.eu is not available at TR-FC1-ULAKBIM in fedcloudclient
[.] Checking VO cloud.egi.eu at UA-BITP
[-] WARNING: VO cloud.egi.eu is not available at UA-BITP in AppDB
[-] WARNING: VO cloud.egi.eu is not available at UA-BITP in fedcloudclient
[.] Checking VO cloud.egi.eu at UNIV-LILLE
[-] WARNING: VO cloud.egi.eu is not available at UNIV-LILLE in AppDB
[-] WARNING: VO cloud.egi.eu is not available at UNIV-LILLE in fedcloudclient
[.] Checking VO cloud.egi.eu at UPV-GRyCAP
[-] WARNING: VO cloud.egi.eu is not available at UPV-GRyCAP in AppDB
[-] WARNING: VO cloud.egi.eu is not available at UPV-GRyCAP in fedcloudclient
[.] Checking VO cloud.egi.eu at WALTON-CLOUD
[-] WARNING: VO cloud.egi.eu is not available at WALTON-CLOUD in AppDB
[-] WARNING: VO cloud.egi.eu is not available at WALTON-CLOUD in fedcloudclient
[.] Checking VO cloud.egi.eu at fedcloud.srce.hr
[-] WARNING: VO cloud.egi.eu is not available at fedcloud.srce.hr in AppDB
[-] WARNING: VO cloud.egi.eu is not available at fedcloud.srce.hr in fedcloudclient
[.] Checking VO cloud.egi.eu at EODC
[-] WARNING: VO cloud.egi.eu is not available at EODC in AppDB
[-] WARNING: VO cloud.egi.eu is not available at EODC in fedcloudclient
[.] Checking VO cloud.egi.eu at ELKH-CLOUD
[-] WARNING: VO cloud.egi.eu is not available at ELKH-CLOUD in AppDB
[-] WARNING: VO cloud.egi.eu is not available at ELKH-CLOUD in fedcloudclient
```

## Useful links

- [OpenStack API](https://docs.openstack.org/api-ref/)
- [OpenStack API examples](https://docs.openstack.org/keystone/pike/api_curl_examples.html)
