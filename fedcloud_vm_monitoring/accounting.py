"""Class for interaction with the accounting portal"""

import datetime
import numbers

import httpx

ACCOUNTING_URL = "https://accounting.egi.eu/"
SITE_VO_ACCOUNTING = ("cloud/sum_elap_processors/SITE/VO/"
                      "{start_year}/{start_month}/{end_year}/{end_month}"
                      "/all/onlyinfrajobs/JSON/")


class Accounting:
    def __init__(self):
        self._data = {}

    def _get_accounting_data(self):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=90)
        print(start)
        url = ACCOUNTING_URL + SITE_VO_ACCOUNTING.format(
            start_year=start.year,
            start_month=start.month,
            end_year=today.year,
            end_month=today.month,
        )
        # accounting generates a redirect here
        r = httpx.get(url, follow_redirects=True)
        self._data = r.json()
        return self._data

    def site_vos(self, site):
        if not self._data:
            self._get_accounting_data()
        for col in self._data:
            if col["id"] == site:
                return set(
                    [
                        vo[0]
                        for vo in col.items()
                        if isinstance(vo[1], numbers.Number)
                        and vo[1] != 0
                        and vo[0] not in ["Total", "Percent"]
                    ]
                )
        return set([])

    def all_sites(self):
        if not self._data:
            self._get_accounting_data()
        for col in self._data:
            if col["id"] == "xlegend":
                return [site[1] for site in col.items() if site[0] != "id"]
        return []
