"""Classes to interact with the GOCDB"""

import re
import datetime
import httpx
import pprint
import xmltodict
import numbers
import yaml

GOC_PUBLIC_URL = "https://goc.egi.eu/gocdbpi/public/"
GOC_PRIVATE_URL = "https://goc.egi.eu/gocdbpi/private/"
SERVICE_TYPES = ["org.openstack.nova"]
SLA_GROUP_RE = r"EGI_(.*)_SLA"

class GOCDB:
    def __init__(self):
        self._cache = {}
        self.queries = 0
        self.sla_vos = set()

    def get_sla_groups(self, cert_file, scope="EGI,SLA"):
        client = httpx.Client(cert=cert_file)
        params = {"method": "get_service_group", "scope": scope}
        response = client.get(GOC_PRIVATE_URL, params=params)
        self.queries += 1
        groups = xmltodict.parse(response.text)["results"]["SERVICE_GROUP"]
        return groups

    def get_sites_slas(self, cert_file, vo_map):
        groups = self.get_sla_groups(cert_file)
        all_vos = []
        for vo in vo_map.values():
            if vo:
                all_vos.extend(vo)
        self.sla_vos = set(all_vos)

        sites = {}
        for group in groups:
            m = re.search(SLA_GROUP_RE, group["NAME"])
            if not m:
                continue
            sla_name = m.group(1)
            vos = vo_map.get(sla_name)
            endpoints = group.get("SERVICE_ENDPOINT", [])
            if not isinstance(endpoints, list):
                endpoints = [endpoints]
            for endpoint in endpoints:
                svc = self.get_endpoint_site(endpoint)
                if svc:
                    for site in svc["SITENAME"]:
                        site_info = sites.get("site", dict())
                        site_info[sla_name] = {
                            "vos": set(vos or [])
                        }
                        sites[site] = site_info
        return sites

    def get_endpoint_site(self, endpoint):
        key = endpoint["@PRIMARY_KEY"]
        service = {}
        if key in self._cache:
            return self._cache[key]
        if endpoint.get("SERVICE_TYPE", "") not in SERVICE_TYPES:
            return None
        params = {"method": "get_service"}
        if "HOSTNAME" in endpoint:
            params["hostname"] = endpoint["HOSTNAME"]
        if "SERVICE_TYPE" in endpoint:
            params["service_type"] = endpoint["SERVICE_TYPE"]
        r = httpx.get(GOC_PUBLIC_URL, params=params)
        self.queries += 1
        if r.text:
            results = xmltodict.parse(r.text).get("results", {})
            if results:
                service = results.get("SERVICE_ENDPOINT", {})
        if service:
            self._cache[key] = service
        return service
