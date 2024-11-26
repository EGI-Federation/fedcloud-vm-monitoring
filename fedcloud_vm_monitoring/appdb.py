"""AppDB queries"""

import requests

sites_supporting_vo_query = """
{
  sites(filter: {cloudComputingShares: {VO: {eq: "%s"}}}) {
    items {
      name
    }
  }
}"""

vos_in_site_query = """
{
  sites(filter: {name: {eq: "%s"}}) {
    items {
      cloudComputingShares {
        items {
          VO
        }
      }
    }
  }
}"""


class AppDB:
    graphql_url = "https://is.appdb.egi.eu/graphql"

    def __init__(self):
        self.sites = {}

    def get_sites_for_vo(self, vo):
        params = {"query": sites_supporting_vo_query % vo}
        r = requests.get(
            self.graphql_url, params=params, headers={"accept": "application/json"}
        )
        r.raise_for_status()
        data = r.json()["data"]["sites"]["items"]
        return [i["name"] for i in data]

    def vo_check(self, site, vo):
        if not self.sites:
            self.sites = self.get_sites_for_vo(vo)
        return site in self.sites

    def get_vo_for_site(self, site):
        params = {"query": vos_in_site_query % site}
        r = requests.get(
            self.graphql_url, params=params, headers={"accept": "application/json"}
        )
        r.raise_for_status()
        sites_items = r.json()["data"]["sites"]["items"]
        if sites_items:
            data = sites_items.pop()["cloudComputingShares"]["items"]
        else:
            return []
        return [i["VO"] for i in data]
