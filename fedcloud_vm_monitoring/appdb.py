"""AppDB queries"""

import requests

site_query = """
{
  sites(filter: {cloudComputingShares: {VO: {eq: "%s"}}}) {
    items {
      name
    }
  }
}"""


class AppDB:
    graphql_url = "https://is.appdb.egi.eu/graphql"

    def __init__(self, vo):
        self.vo = vo
        self.sites = {}

    def get_sites_for_vo(self):
        params = {"query": site_query % self.vo}
        r = requests.get(
            self.graphql_url, params=params, headers={"accept": "application/json"}
        )
        r.raise_for_status()
        data = r.json()["data"]["sites"]["items"]
        return [i["name"] for i in data]

    def vo_check(self, site):
        if not self.sites:
            self.sites = self.get_sites_for_vo()
        return site in self.sites
