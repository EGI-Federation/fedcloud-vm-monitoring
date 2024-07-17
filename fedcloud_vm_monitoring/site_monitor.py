"""Monitor VM instances running in the provider"""

import ipaddress
from collections import defaultdict
from datetime import datetime, timezone

import click
import ldap3
import paramiko
from dateutil.parser import parse
from fedcloudclient.openstack import fedcloud_openstack
from fedcloudclient.sites import find_endpoint_and_project_id
from ldap3.core.exceptions import LDAPException
from paramiko import SSHException


class SiteMonitorException(Exception):
    pass


class SiteMonitor:
    """Helper class to call fedcloudclient easily"""

    color_maps = defaultdict(lambda: "red", ACTIVE="green", BUILD="yellow")
    # at least 1GB per core
    min_ram_cpu_ratio = 1024
    min_secgroup_instance_ratio = 3
    min_ip_instance_ratio = 1

    def __init__(self, site, vo, token, max_days, ldap_config={}):
        self.site = site
        self.vo = vo
        self.token = token
        self.max_days = max_days
        self.ldap_config = ldap_config
        self.flavors = {}
        self.users = defaultdict(lambda: {})
        self.user_emails = {}
        self.now = datetime.now(timezone.utc)

    def _run_command(self, command, do_raise=True, json_output=True, scoped=True):
        vo = self.vo if scoped else None
        error_code, result = fedcloud_openstack(
            self.token, self.site, vo, command, json_output=json_output
        )
        if error_code != 0:
            if do_raise:
                raise SiteMonitorException(result)
            else:
                click.echo(" ".join([click.style("WARNING:", fg="yellow"), result]))
                return {}
        return result

    def get_user(self, user_id):
        if not self.users:
            all_users = []
            try:
                command = ("user", "list")
                all_users = self._run_command(command)
            except SiteMonitorException:
                try:
                    # trick fedcloudclient to give us what we need
                    command = ("token", "issue")
                    token = self._run_command(command, scoped=False)
                    command = ("user", "show", token["user_id"])
                    my_user = self._run_command(command, scoped=True)
                    # now we have the domain, can get all users
                    command = ("user", "list", "--os-domain-id", my_user["domain_id"])
                    all_users = self._run_command(command, scoped=False)
                except SiteMonitorException as e:
                    click.secho(f"WARNING: Unable to get user list: {e}", fg="yellow")
            for user in all_users:
                self.users[user["ID"]] = user
        return self.users[user_id]

    def get_flavor(self, flavor_name):
        if flavor_name in self.flavors:
            return self.flavors[flavor_name]
        command = ("flavor", "list", "--long")
        result = self._run_command(command)
        for flv in result:
            self.flavors[flv["Name"]] = flv
        if flavor_name not in self.flavors:
            return {}
        return self.flavors[flavor_name]

    def get_vm_image_volume_show(self, volume_id):
        try:
            cmd = ("volume", "show", volume_id, "--format", "json")
            result = self._run_command(cmd)
            if ("volume_image_metadata" in result) and (
                "sl:osname" and "sl:osversion" in result["volume_image_metadata"]
            ):
                return (
                    result["volume_image_metadata"]["sl:osname"]
                    + " "
                    + result["volume_image_metadata"]["sl:osversion"]
                )
            elif ("volume_image_metadata" in result) and (
                "os_distro" and "os_version" in result["volume_image_metadata"]
            ):
                return (
                    result["volume_image_metadata"]["os_distro"]
                    + " "
                    + result["volume_image_metadata"]["os_version"]
                )
            elif ("volume_image_metadata" in result) and (
                "image_name" in result["volume_image_metadata"]
            ):
                return result["volume_image_metadata"]["image_name"]
            else:
                return "image name not found"
        except SiteMonitorException:
            return "image name not found"

    def get_vm_image_server_show(self, vm_id):
        try:
            cmd = ("server", "show", vm_id, "--format", "json")
            result = self._run_command(cmd)
            if len(result["attached_volumes"]) > 0:
                return self.get_vm_image_volume_show(
                    result["attached_volumes"][0]["id"]
                )
            else:
                return "image name not found"
        except SiteMonitorException:
            return "image name not found"

    def get_vm_image(self, vm_id, image_name, image_id):
        """Commands to get VM images:
        1. openstack server list --long -c "ID" -c "Name" -c "Image Name" -c "Image ID"

        If "Image Name" is available, print it. If not, get details from image:
        2. openstack image show <image-id>

        If not, get details from attached volumes:
        3a. openstack server show <vm-id>
        3b. openstack volume show <volume-id>

        Parameters
        ----------
        vm_id: str
            The ID of the VM
        image_name: str
            The name of the VM image
        image_id: str
            The ID of the VM image

        Returns
        -------
        str
            a string with the name of the image
        """
        if (len(image_name) > 0) and ("booted from volume" not in image_name):
            return image_name
        else:
            try:
                cmd = ("image", "show", image_id, "--format", "json")
                result = self._run_command(cmd)
                if "sl:osname" and "sl:osversion" in result["properties"]:
                    return (
                        result["properties"]["sl:osname"]
                        + " "
                        + result["properties"]["sl:osversion"]
                    )
                else:
                    return self.get_vm_image_server_show(vm_id)
            except SiteMonitorException:
                return self.get_vm_image_server_show(vm_id)

    def get_vms(self):
        command = ("server", "list", "--long")
        return self._run_command(command)

    def get_vm(self, vm):
        command = ("server", "show", vm["ID"])
        return self._run_command(command)

    def delete_vm(self, vm):
        click.echo(
            f"[-] Deleting of the instance [{click.style(vm['ID'], fg='red')}] in progress..."
        )
        command = ("server", "delete", vm["ID"])
        # this won't work as it does not accept a --json option :(
        self._run_command(command, do_raise=False, json_output=False)

    def get_user_email(self, egi_user):
        if not self.ldap_config:
            return ""
        # TODO: this is untested code
        if not self.user_emails:
            try:
                # get the emails
                server = ldap3.Server(self.ldap_config["server"], get_info=ldap3.ALL)
                conn = ldap3.Connection(
                    server,
                    self.ldap_config["username"],
                    password=self.ldap_config["password"],
                    auto_bind=True,
                )
                conn.search(
                    self.ldap_config["base_dn"],
                    self.ldap_config["search_filter"],
                    attributes=["*"],
                )
                for entry in conn.entries:
                    self.user_emails[entry["voPersonID"].value] = entry["mail"].value
            except LDAPException as e:
                click.secho(f"WARNING: LDAP error: {e}", fg="yellow")
        if egi_user not in self.user_emails:
            return f"{egi_user} not found in LDAP, has VO membership expired?"
        return self.user_emails[egi_user]

    def get_public_ip(self, ip_addresses):
        result = ""
        for ip in ip_addresses:
            if ipaddress.ip_address(ip).is_global:
                result = ip
        return result

    def get_sshd_version(self, ip_addresses):
        public_ip = self.get_public_ip(ip_addresses)
        if len(public_ip) > 0:
            try:
                ssh = paramiko.Transport((public_ip, 22))
                ssh.start_client()
                result = ssh.remote_version
                ssh.close()
                return result
            except SSHException:
                return "SSHException: could not retrieve SSH version"
        else:
            return "No public IP available to check SSH version."

    def process_vm(self, vm):
        vm_info = self.get_vm(vm)
        flv = self.get_flavor(vm["Flavor"])
        vm_ips = []
        for net, addrs in vm["Networks"].items():
            vm_ips.extend(addrs)
        sshd_version = self.get_sshd_version(vm_ips)
        created = parse(vm_info["created_at"])
        elapsed = self.now - created
        output = [
            ("instance name", vm["Name"]),
            ("instance id", vm["ID"]),
            ("status", click.style(vm["Status"], fg=self.color_maps[vm["Status"]])),
            ("ip address", " ".join(vm_ips)),
            ("SSH version", sshd_version),
        ]
        if flv:
            output.append(
                (
                    "flavor",
                    f"{flv['Name']} with {flv['VCPUs']} vCPU cores, {int(flv['RAM']/1024)} "
                    f"GB of RAM and {flv['Disk']} GB of local disk",
                )
            )
        output.append(
            ("VM image", self.get_vm_image(vm["ID"], vm["Image Name"], vm["Image ID"]))
        )
        output.append(("created at", vm_info["created_at"]))
        output.append(("elapsed time", elapsed))
        user_id = vm_info["user_id"]
        output.append(("user", user_id))
        user = self.get_user(user_id)
        if user:
            if "email" not in user:
                self.users[user_id]["email"] = self.get_user_email(
                    user.get("Name", None)
                )
            output.append(("egi user", user.get("Name", "")))
            output.append(("email", user.get("email", "")))
        orchestrator = vm_info["properties"].get("eu.egi.cloud.orchestrator", None)
        if orchestrator == "es.upv.grycap.im":
            output.append(
                ("IM id", vm_info["properties"].get("eu.egi.cloud.orchestrator.id", ""))
            )
        return {"ID": vm["ID"], "output": output, "elapsed": elapsed}

    def vm_monitor(self, delete=False):
        all_vms = self.get_vms()
        if not all_vms:
            click.secho("- No VM instances found in the resource provider", fg="yellow")
            return
        click.echo(
            f"[+] Total VM instance(s) running in the resource provider = {len(all_vms)}"
        )
        vms_info = []
        with click.progressbar(all_vms, label="Getting VMs information") as vms:
            for vm in vms:
                vms_info.append(self.process_vm(vm))
        for i, vm in enumerate(vms_info):
            click.echo(f"[+] VM #{i:<2} {'-'*50}")
            for line in vm["output"]:
                click.echo(f"    {line[0]:<14} = {line[1]}")
            if vm["elapsed"].days >= self.max_days:
                click.secho(
                    "[-] WARNING The VM instance elapsed time exceed the max offset!",
                    fg="yellow",
                )
                if delete:
                    if click.confirm("Do you want to delete the instance?"):
                        self.delete_vm(vm)

    def vo_check(self):
        endpoint, _, _ = find_endpoint_and_project_id(self.site, self.vo)
        return endpoint is not None

    def get_quota(self):
        command = ("quota", "show")
        return self._run_command(command, do_raise=False)

    def show_quotas(self):
        quota = self.get_quota()
        if not quota:
            return
        resources = [
            "cores",
            "instances",
            "ram",
            "floating-ips",
            "secgroup-rules",
            "secgroup",
        ]
        quota_info = {}
        for r in quota:
            if r["Resource"] in resources:
                if r["Resource"] == "ram":
                    quota_info[r["Resource"] + " (GB)"] = int(r["Limit"] / 1024)
                else:
                    quota_info[r["Resource"]] = r["Limit"]
        for k, v in quota_info.items():
            click.echo(f"    {k:<14} = {v}")
        # checks on quota
        if quota_info.get("ram", 1) / quota_info.get("cpu", 1) < self.min_ram_cpu_ratio:
            click.secho(
                f"[-] WARNING: Less than {int(self.min_ram_cpu_ratio/1024)} GB RAM per available CPU",
                fg="yellow",
            )
        if (
            quota_info.get("secgroup", 1) / quota_info.get("instances", 1)
            < self.min_secgroup_instance_ratio
        ):
            click.secho(
                f"[-] WARNING: Less than {self.min_secgroup_instance_ratio} security groups per instance",
                fg="yellow",
            )
        if (
            quota_info.get("floating-ips", 1) / quota_info.get("instances", 1)
            < self.min_ip_instance_ratio
        ):
            click.secho(
                f"[-] WARNING: Less than {self.min_ip_instance_ratio} floating IPs per instance",
                fg="yellow",
            )
