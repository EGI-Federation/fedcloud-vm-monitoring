"""Monitor VM instances running in the provider"""

import sys

import click
from fedcloudclient.sites import list_sites

from fedcloud_vm_monitoring.site_monitor import SiteMonitor
from fedcloud_vm_monitoring.appdb import AppDB


@click.command()
@click.option("--site", help="site name")
@click.option("--vo", default="vo.access.egi.eu", help="vo name")
@click.option("--token", help="access token")
@click.option("--max-days", default=90, help="max number of days for running instances")
@click.option("--delete", default=False, help="ask for deletion of VMs")
@click.option("--show-quotas", default=True, help="show quotas for VO")
def main(site, vo, token, max_days, delete, show_quotas):
    sites = [site] if site else list_sites()
    appdb = AppDB(vo)
    for s in sites:
        click.secho(f"[.] Checking VO {vo} at {s}", fg="blue", bold=True)
        if not appdb.vo_check(s):
            click.secho(
                f"[-] WARNING: VO {vo} is not available at {s} in AppDB", fg="yellow"
            )
        site_monitor = SiteMonitor(s, vo, token, max_days)
        if not site_monitor.vo_check():
            click.secho(
                f"[-] WARNING: VO {vo} is not available at {s} in fedcloudclient",
                fg="yellow",
            )
            continue
        try:
            site_monitor.vm_monitor(delete)
        except Exception as e:
            click.echo(" ".join([click.style("ERROR:", fg="red"), str(e)]), err=True)
        if show_quotas:
            click.echo("[+] Quota information:")
            site_monitor.show_quotas()
        # TODO: volumes, ips, should look for those older than X days
        #       and not attached to any VM for deletion
        # site_monitor.vol_monitor()
        # site_monitor.ip_monitor()


if __name__ == "__main__":
    main()
