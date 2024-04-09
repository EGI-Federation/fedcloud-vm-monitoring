"""Monitor VM instances running in the provider"""

import click
from fedcloud_vm_monitoring.appdb import AppDB
from fedcloud_vm_monitoring.site_monitor import SiteMonitor, SiteMonitorException
from fedcloudclient.decorators import oidc_params
from fedcloudclient.sites import list_sites



@click.command()
@oidc_params
@click.option("--site", help="Restrict the monitoring to the site provided")
@click.option("--vo", default="vo.access.egi.eu", help="VO name to monitor")
@click.option(
    "--max-days",
    default=90,
    help="Maximum number of days instances can be running for triggering deletion",
)
@click.option("--delete", default=False, is_flag=True, help="Ask for deletion of VMs")
@click.option("--show-quotas", default=True, help="Show quotas for VO")
@click.option(
    "--ldap-server",
    default="ldaps://ldap.aai.egi.eu:636",
    help="LDAP server for VO membership",
)
@click.option(
    "--ldap-base-dn",
    default="ou=people,dc=ldap,dc=aai,dc=egi,dc=eu",
    help="LDAP base DN",
)
@click.option("--ldap-user", help="LDAP user")
@click.option("--ldap-password", help="LDAP password")
@click.option(
    "--ldap-search-filter",
    default="(isMemberOf=CO:COU:vo.access.egi.eu:members)",
    help="LDAP search filter",
)
def main(
    access_token,
    site,
    vo,
    max_days,
    delete,
    show_quotas,
    ldap_server,
    ldap_base_dn,
    ldap_user,
    ldap_password,
    ldap_search_filter,
):
    ldap_config = {}
    if ldap_user and ldap_password:
        ldap_config.update(
            {
                "server": ldap_server,
                "username": ldap_user,
                "password": ldap_password,
                "base_dn": ldap_base_dn,
                "search_filter": ldap_search_filter,
            }
        )
    sites = [site] if site else list_sites()
    appdb = AppDB(vo)
    for s in sites:
        click.secho(f"[.] Checking VO {vo} at {s}", fg="blue", bold=True)
        if not appdb.vo_check(s):
            click.secho(
                f"[-] WARNING: VO {vo} is not available at {s} in AppDB", fg="yellow"
            )
        site_monitor = SiteMonitor(s, vo, access_token, max_days, ldap_config)
        if not site_monitor.vo_check():
            click.secho(
                f"[-] WARNING: VO {vo} is not available at {s} in fedcloudclient",
                fg="yellow",
            )
            continue
        try:
            site_monitor.vm_monitor(delete)
        except SiteMonitorException as e:
            click.echo(" ".join([click.style("ERROR:", fg="red"), str(e)]), err=True)
        if show_quotas:
            click.echo("[+] Quota information:")
            site_monitor.show_quotas()
        # TODO: volumes, ips, should look for those older than X days
        #       and not attached to any VM for deletion
        # site_monitor.vol_monitor()
        # site_monitor.ip_monitor()
