#!/usr/bin/env python3
#
#  Copyright 2021 EGI Foundation
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json
import requests
import datetime as dt
from utils import load_provider_settings, colourise, highlight, get_credentials
from pytz import timezone
from pyGetScopedToken import get_OIDC_Token, get_scoped_Token, get_unscoped_Token


__author__    = "Giuseppe LA ROCCA"
__email__     = "giuseppe.larocca@egi.eu"
__version__   = "$Revision: 1.0.1"
__date__      = "$Date: 27/04/2021 18:40:27"
__copyright__ = "Copyright (c) 2021 EGI Foundation"
__license__   = "Apache Licence v2.0"


# This configuration file contains the settings of EFI cloud providers to be checked.
PROVIDERS_SETTINGS_FILENAME = "providers-settings.ini"

# Set the max elapsed time (in hours) for a running instance in the EGI FedCloud infrastructure
# Considering as offset 1 mounth = 30 days * 24h = 720 hours
offset = 720


def get_running_instances(compute_url, project_id, token):
    ''' Get the list of running instances in the provider '''

    url = "%s/%s/servers" %(compute_url, project_id)
    headers = {'X-Auth-Token': '%s' %token, 'Content-type': 'application/json'}
   
    curl = requests.get(url=url, headers=headers)
    if curl.status_code == 200:
       data = curl.json()
    else:
       raise RuntimeError("Unable to get running instances!")

    return data


def get_instance_metadata(instance_id, token):
    ''' Retrieve details about the running instance '''

    url = "%s" %instance_id
    headers = {'X-Auth-Token': '%s' %token, 'Content-type': 'application/json'}

    curl = requests.get(url=url, headers=headers)
    data = curl.json()

    return data


def get_instance_ip(instance_id, token):
    ''' Retrieve the IPs of the running instance '''

    url = "%s/ips" %instance_id
    headers = {'X-Auth-Token': '%s' %token, 'Content-type': 'application/json'}

    curl = requests.get(url=url, headers=headers)
    if curl.status_code == 200:
       data = curl.json()

    return data


def get_flavor(compute_url, flavor_id, token):
    ''' Retrieve the flavor details of the running instance '''

    url = "%s/flavors/%s" %(compute_url, flavor_id)
    headers = {'X-Auth-Token': '%s' %token, 'Content-type': 'application/json'}

    curl = requests.get(url=url, headers=headers)
    if curl.status_code == 200:
       data = curl.json()
    else:
       data = ""

    return [curl.status_code, data]


def get_user(identity_url, user_id, token):
    ''' Retrieve the real user from KeyStone '''

    url = "%s/users/%s" %(identity_url, user_id)
    headers = {'X-Auth-Token': '%s' %token, 'Content-type': 'application/json'}

    curl = requests.get(url=url, headers=headers)
    data = curl.json()

    if curl.status_code == 403:
       text="  WARNING\t= User not authorized to perform the requested action: 'identity:get_user'"
       print(colourise("yellow", text))
       data=""

    return data


def delete_instance(instance_id, token):
    ''' Remove server instance from the cloud provider '''

    try:
         url = "%s" %instance_id
         headers = {'X-Auth-Token': '%s' %token, 'Content-type': 'application/json'}

         delete_files = raw_input('Do you want to remove the running VM (y/n) ? ')
         if delete_files in ['Y', 'y', 'Yes', 'yes', 'YES', 'true', 'TRUE', 'True']:
            curl = requests.delete(url=url, headers=headers)

            if curl.status_code == 204:
               print ("[DONE] Server instance successfully removed from the provider.")

            if curl.status_code == 409:
               text="WARNING: Unable to remove the running VM. The VM is locked by the user."
               print(colourise("red", text))
            else:
               print("Aborting ...")

    except Exception as error:
           pass


def main():
    
    # Get the user's credentials
    creds = get_credentials()
    #print("os_protocol = %s " % creds['os_protocol'])
    #print("os_identity_api_version = %s " % creds['os_identity_api_version'])
    #print("os_identity_provider = %s " % creds['os_identity_provider'])
    #print("os_auth_type = %s " % creds['os_auth_type'])
    #print("checkin_client_id = %s " % creds['checkin_client_id'])
    #print("checkin_client_secret = %s " % creds['checkin_client_secret'])
    #print("checkin_refresh_token = %s " % creds['checkin_refresh_token'])
    #print("checkin_auth_url = %s " % creds['checkin_auth_url'])

    # Initialize the OIDC token from the EGI AAI Check-In service.
    token = get_OIDC_Token(creds['checkin_auth_url'], 
                           creds['checkin_client_id'], 
                           creds['checkin_client_secret'], 
                           creds['checkin_refresh_token'])

    # Loading the configuration settings of the EGI training providers
    providers = load_provider_settings(PROVIDERS_SETTINGS_FILENAME)

    for index in range(0, len(providers)):
        # Parsing the providers JSON object
        provider_name = providers[index]["provider"]["name"]
        provider_identity = providers[index]["provider"]["identity"]
        provider_compute = providers[index]["provider"]["compute"]
        provider_project_id = providers[index]["provider"]["project_id"]

        print("[.] Reading settings of the provider: %s " %provider_name)
        print("%s" %json.dumps(providers[index], indent=4, sort_keys=False))

        # Retrieve an OpenStack scoped token 
        scoped_token = get_scoped_Token(provider_identity,
                       provider_project_id,
                       get_unscoped_Token(provider_identity, token))

        #print(scoped_token)

        # Get the list of the running instances in the selected provider 
        instances = get_running_instances(provider_compute, provider_project_id, scoped_token)
        #print("\n%s" %json.dumps(instances, indent=4, sort_keys=False))

        index=1
        if len(instances['servers'])>0:
           print("\n[+] Total VM instance(s) running in the provider = [#%s]" %len(instances['servers']))
           for index in range(0, len(instances['servers'])):
                if instances['servers'][index]['links']:
                   # Get the instance_id
                   instance_id = instances['servers'][index]['links'][0]['href']
                   # Get the instance metadata
                   vm_details = get_instance_metadata(instance_id, scoped_token) 
                   #print("\n%s" %json.dumps(vm_details, indent=4, sort_keys=False))
                   created = vm_details['server']['created']
                   status = vm_details['server']['status']
                   instance_name = vm_details['server']['name']
    
                   # Retrieve the list of network interfaces of the instance
                   ip_details=get_instance_ip(instance_id, scoped_token)
                   #print("\n%s" %json.dumps(ip_details, indent=4, sort_keys=False))
                   for key in ip_details['addresses']:
                       # Get the nmax of addresses
                       nmax=len(ip_details['addresses'][key])
                       ip_address = ip_details['addresses'][key][nmax-1]['addr']

                   # Retrieve the flavor details
                   flavor_id=vm_details['server']['flavor']['id']
                   flavor_details=get_flavor(provider_compute, flavor_id, scoped_token)
                   #print("\n%s" %json.dumps(flavor_details, indent=4, sort_keys=False))
                   # Check status code from the requests...
                   if flavor_details[0] == 200: 
                      flavor_name=flavor_details[1]['flavor']['name']
                      flavor_vcpus=flavor_details[1]['flavor']['vcpus']
                      flavor_ram=flavor_details[1]['flavor']['ram']
                      flavor_disk=flavor_details[1]['flavor']['disk']

                   # Print VM instance metadata
                   print("_" + "_" * 60)
                   print("- instance name = %s " %instance_name)
                   print("- instance_id   = %s " %instance_id)
                   print("- status        = %s " %status)
                   print("- ip address    = %s " %ip_address)
                   if flavor_details[0] == 200: 
                      print("- image flavor  = %s with %s vCPU cores, %s of RAM and %sGB of local disk " \
                              %(flavor_name, flavor_vcpus, flavor_ram, flavor_disk))
                   print("- created at    = %s " %created)

                   # Check the lifetime of the running instance
                   created = dt.datetime.strptime(created, '%Y-%m-%dT%H:%M:%SZ')
                   created_utc = timezone('UCT').localize(created)
                   time_utc = dt.datetime.now(timezone('UCT'))
                   duration=((time_utc-created_utc).total_seconds()/3600)
                   print("- elapsed time  = %s (hours)" %format(duration, '.2f'))

                   user_id = vm_details['server']['user_id']
                   # Get the (real) user from Keystone
                   user_details = get_user(provider_identity, user_id, scoped_token)

                   if user_details:
                      username = user_details['user']['name']
                      print("- created by    = %s " %username)
                   else:
                      print("- created by    = %s " %user_id)

                   if (status == "ACTIVE"):
                      if (int(duration)>offset):
                          text="\n[-] WARNING: The VM instance elapsed time exceed the max offset!"
                          print(colourise("cyan", text))
                          
                          text="[-] Deleting of the instance [%s] in progress ..."
                          print(highlight("red", text \
                                 %instance_id[-36:len(instance_id)]))
                          delete_instance(instance_id, scoped_token)

                   index=index+1

        else:
              print ("No VMs instances found in the server: %s" %provider_name)
    
        print("")

if __name__ == "__main__":
    main()


