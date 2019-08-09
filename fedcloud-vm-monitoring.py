#!/usr/bin/env python

import requests
import json, os
import ConfigParser
import datetime as dt
from pytz import timezone
from pyGetScopedToken import get_OIDC_Token, get_scoped_Token, get_unscoped_Token

# This configuration file contains the settings of EFI cloud providers to be checked.
training_settings = "providers-settings.ini"

# These are the EGI AAI Check-In settings used to generate a valid access token
client_id = "f33e824a-078d-497b-b700-25b0df7fc5b7"
client_secret = "B80vPK0LVbYuvwRj0Aexs8y0rKgk5XHwYRRq3BCr33ejj33385bzDVcPmSTUkqA2QjMiwWKJDTxvOou7yVV8EA"
refresh_token = "eyJhbGciOiJub25lIn0.eyJleHAiOjE1ODQyNzQxNDYsImp0aSI6IjkzNGMxNTBhLTA4NDQtNDI5ZC05NDJhLTIwMzIxMDgzNzIzMSJ9."
checkin_auth_url = "https://aai.egi.eu/oidc/token"

# Set the max elapsed time (in hours) for a running instance in the EGI FedCloud infrastructure
# Considering as offset 1 mounth = 30 days * 24h = 720 hours
offset = 720

def load(file):
	''' Load cloud providers settings '''
	filename="%s/%s" %(os.environ['PWD'], file)
	providers = []

	# Reading configuration file
	config = ConfigParser.ConfigParser()
	config.read(filename)
	
	for section in config.sections():
		options = config.options(section)

		# Creation of the JSON file
		providers.append({
			"provider": {
				"name": config.get(section,'Name'),
				"country": config.get(section, 'Country'),
				"identity": config.get(section, 'Identity'),
				"compute": config.get(section, 'Compute'),
				"project_id": config.get(section, 'ProjectID')
			}
		})

	return providers


def get_running_instances(compute_url, project_id, token):
	''' Get the list of running instances in the provider '''

	url = "%s/%s/servers" %(compute_url, project_id)

	headers = {'X-Auth-Token': '%s' %token,
                   'Content-type': 'application/json'}

        curl = requests.get(url=url, headers=headers)

        if curl.status_code == 200:
                data = curl.json()
        else:
                raise RuntimeError("Unable to get running instances!")

	return data


def get_instance_metadata(instance_id, token):
	''' Retrieve details about the running instance '''

	url = "%s" %instance_id

	headers = {'X-Auth-Token': '%s' %token,
                   'Content-type': 'application/json'}
		
	curl = requests.get(url=url, headers=headers)
	data = curl.json()

	return data


def get_instance_ip(instance_id, token):
	''' Retrieve the IPs of the running instance '''

	url = "%s/ips" %instance_id

        headers = {'X-Auth-Token': '%s' %token,
                   'Content-type': 'application/json'}

        curl = requests.get(url=url, headers=headers)
        data = curl.json()

        return data


def get_flavor(compute_url, flavor_id, token):
	''' Retrieve the flavor details of the running instance '''

	url = "%s/flavors/%s" %(compute_url, flavor_id)

        headers = {'X-Auth-Token': '%s' %token,
                   'Content-type': 'application/json'}

        curl = requests.get(url=url, headers=headers)
        data = curl.json()

        return data


def get_user(identity_url, user_id, token):
	''' Retrieve the real user from KeyStone '''

	url = "%s/users/%s" %(identity_url, user_id)

	headers = {'X-Auth-Token': '%s' %token,
                   'Content-type': 'application/json'}

	curl = requests.get(url=url, headers=headers)
        data = curl.json()

	if curl.status_code == 403:
		print("WARNING: User not authorized to perform the requested action: 'identity:get_user'")
		data=""

        return data


def delete_instance(instance_id, token):
	''' Remove server instance from the cloud provider '''

	try:
		url = "%s" %instance_id

		headers = {'X-Auth-Token': '%s' %token,
                	   'Content-type': 'application/json'}

		delete_files = raw_input('Do you want to remove the running VM (y/n) ? ')
		if delete_files in ['Y', 'y', 'Yes', 'yes', 'YES', 'true', 'TRUE', 'True']:
			curl = requests.delete(url=url, headers=headers)

			if curl.status_code == 204:
				print ("[DONE] Server instance successfully removed from the provider.")

			if curl.status_code == 409:
				print ("WARNING: Unable to remove the running VM. The VM is locked by the user.")
		else:
			print("Aborting ...")

        except Exception as error:
		pass


def main():
	
	# Initialize the OIDC token from the EGI AAI Check-In service.
        token = get_OIDC_Token(checkin_auth_url,
        			client_id,
                                client_secret,
                                refresh_token)

	# Loading the configuration settings of the EGI training providers
        providers = load(training_settings)
	print("")

	for index in range(0, len(providers)):
		# Parsing the providers JSON object
		provider_name = providers[index]["provider"]["name"]
		provider_identity = providers[index]["provider"]["identity"]
		provider_compute = providers[index]["provider"]["compute"]
		provider_project_id = providers[index]["provider"]["project_id"]

		print("[.] Reading the configuration settings of the cloud provider: %s " %provider_name)
        	print("\n%s" %json.dumps(providers[index], indent=4, sort_keys=False))

	        # Retrieve an OpenStack scoped token 
        	scoped_token = get_scoped_Token(provider_identity,
                	       provider_project_id,
                               get_unscoped_Token(provider_identity, 
                               token))

		#print(scoped_token)

		# Get the list of the running instances in the selected provider 
		instances = get_running_instances(provider_compute, provider_project_id, scoped_token)
        	#print("\n%s" %json.dumps(instances, indent=4, sort_keys=False))
	        
		if len(instances['servers'])>0:
			
			print("\n[+] Get running instance(s) [#%s] from the provider ..." %len(instances['servers']))

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
					
					user_id = vm_details['server']['user_id']
					# Get the (real) user from Keystone
					user_details = get_user(provider_identity, user_id, scoped_token)

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
					flavor_name=flavor_details['flavor']['name']
					flavor_vcpus=flavor_details['flavor']['vcpus']
					flavor_ram=flavor_details['flavor']['ram']
					flavor_disk=flavor_details['flavor']['disk']
					
				       	# Print instance metadata
					print("\n[ Reporting ] _" + "_" * 116)
                                        print("[-] instance name = %s " %instance_name)
                                        print("[-] instance_id   = %s " %instance_id)
                                        print("[-] status        = %s " %status)
                                        print("[-] ip address    = %s " %ip_address)
                                        print("[-] image flavor  = %s with %s vCPU cores, %s of RAM and %sGB of local disk " \
					%(flavor_name, flavor_vcpus, flavor_ram, flavor_disk))
                                        print("[-] created at    = %s " %created)

					if user_details:
						username = user_details['user']['name']
						print("[-] created by    = %s " %username)
					else:
						print("[-] created by    = %s " %user_id)

					# Check the lifetime of the running instance
					created = dt.datetime.strptime(created, '%Y-%m-%dT%H:%M:%SZ')
					created_utc = timezone('UCT').localize(created)
					time_utc = dt.datetime.now(timezone('UCT'))
					duration=((time_utc-created_utc).total_seconds()/3600)
					print("[-] elapsed time  = %s (hours)" %format(duration, '.2f'))

					if (status == "ACTIVE"):
						if (int(duration)>offset):
							print("\nWARNING: The instance elapsed time exceed the max offset!")
							print("[-] Deleting of the instance [%s] in progress ..." \
							%instance_id[-36:len(instance_id)])
							delete_instance(instance_id, scoped_token)

		else:
			print ("No available instances found in the server: %s " %provider_name)

		print("")
		

if __name__ == "__main__":
        main()

