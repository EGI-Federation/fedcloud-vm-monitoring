"""Monitor Accounting status"""

import importlib

import click
import yaml
from fedcloud_vm_monitoring.accounting import Accounting
from fedcloud_vm_monitoring.appdb import AppDB
from fedcloud_vm_monitoring.goc import GOCDB


def check_site_slas(site, site_slas, goc, acct, appdb):
    click.echo(f"[-] Checking site {site}")
    sla_vos = set()
    appdb_vos = set(appdb.get_vo_for_site(site))
    if site not in site_slas:
        click.echo(f"[I] {site} is not present in any SLA")
    else:
        for sla_name, sla in site_slas[site].items():
            sla_vos = sla_vos.union(sla["vos"])
            accounted_vos = sla["vos"].intersection(acct.site_vos(site))
            if accounted_vos:
                click.echo(
                    f"[OK] SITE {site} has accouting info for SLA {sla_name} ({accounted_vos})"
                )
            else:
                click.echo(
                    f"[ERR] SITE {site} has no accouting info for SLA {sla_name}"
                )
            info_vos = sla["vos"].intersection(appdb_vos)
            if info_vos:
                click.echo(
                    f"[OK] SITE {site} has configured {info_vos} for SLA {sla_name}"
                )
            else:
                click.echo(f"[ERR] SITE {site} has no configured VO for SLA {sla_name}")
    click.echo("[-] Checking aditional VOs")
    # Now check which VOs are being reported without a SLA
    if not sla_vos:
        sla_vos = goc.sla_vos
    non_sla_vos = acct.site_vos(site) - sla_vos.union(set(["ops"]))
    if non_sla_vos:
        click.echo(
            f"[W] Site {site} has accounting for VOs {non_sla_vos} but non covered by SLA"
        )
    if "ops" not in acct.site_vos(site):
        click.echo(f"[W] SITE {site} has accounting for ops")
    non_sla_appdb_vos = appdb_vos - sla_vos.union(set(["ops"]))
    if non_sla_vos:
        click.echo(
            f"[W] Site {site} has VOs {non_sla_appdb_vos} configured but non covered by SLA"
        )
    if "ops" not in appdb_vos:
        click.echo(f"[W] SITE {site} has no configuration for ops")


@click.command()
@click.option("--site", help="Site to check")
@click.option("--user-cert", required=True, help="User certificate (for GOCDB queries)")
@click.option("--vo-map-file", help="SLA-VO mapping file")
def main(
    site,
    user_cert,
    vo_map_file,
):
    if vo_map_file:
        with open(vo_map_file) as f:
            vo_map_src = f.read()
    else:
        vo_map_src = importlib.resources.read_text(
            "fedcloud_vm_monitoring.data", "vos.yaml"
        )
    vo_map = yaml.load(vo_map_src, Loader=yaml.SafeLoader)
    acct = Accounting()
    goc = GOCDB()
    appdb = AppDB()
    slas = goc.get_sites_slas(user_cert, vo_map)

    print(slas)
    if site:
        check_site_slas(site, slas, goc, acct, appdb)
    else:
        for site in acct.all_sites():
            check_site_slas(site, slas, goc, acct, appdb)
