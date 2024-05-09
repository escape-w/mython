#!/usr/bin/env python3

import argparse
import os
import re
import json
from pathlib import Path
import requests

"""
    Utility to onboard user in Azure Github
"""

class Styl:
    GREEN = "\033[32m"
    RESET = "\033[0m"
    RED = '\033[31m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'

def get_token(AMBaseURL,client_id,client_secret):

    url = f"{AMBaseURL}/oauth2/realms/root/realms/machine2machine/access_token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "machine2machine",
        f"client_{client_id}": ""
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=data, headers=headers)


    return response.json()

def get_tickets(SNOWUrl,token,ticket_type):

    #url = f"https://{SNOWUrl}.service-now.com/api/xyzag/v1/now_api/incident"
    url = f"https://{SNOWUrl}.service-now.com/api/xyzag/v1/now_api/{ticket_type}"
    headers = {
        "Content-Type"  : "application/json",
        "Authorization" : f"id_token {token}"
    }
    
    response = requests.get(url, headers=headers)


    return response.json()

if __name__ == "__main__":
    WORK_DIR=os.path.dirname(os.path.realpath(__file__))
    #args = parse_options()

    CONFIG_FILE = Path(WORK_DIR + "/config/.env.json")
    assert CONFIG_FILE.exists(), "config.json must present in config directory"

    config = json.load(open(CONFIG_FILE))
    
    token=get_token(config['AMBaseURL'],config['client_id'],config['client_secret'])

    inc_tickets = get_tickets(config['SNOWUrl'],token['access_token'],'incident')
    print(inc_tickets)

    pbi_tickets = get_tickets(config['SNOWUrl'],token['access_token'],'problem')
    print(pbi_tickets)

    chg_tickets = get_tickets(config['SNOWUrl'],token['access_token'],'change_request')
    print(chg_tickets)

    # sorted_incidents = sorted(tickets['result'], key=lambda x: x['number'])

    # for incident in sorted_incidents:
    #     print(incident['number'], incident['priority'],incident['service_offering']['name'],incident['short_description'],incident['active'],incident['caller_id']['name'])


    # print(f"{Styl.GREEN}Ticket Orbit-Platform-CICD{Styl.RESET}\n"
    #       f"{Styl.YELLOW}--------------------------------------------------{Styl.RESET}"
    #       )
    # for incident in sorted_incidents:
    #     if incident['service_offering']['name'] == 'Orbit-Platform-CICD':
    #         print(incident['number'], incident['priority'])
    
    # print(f"{Styl.GREEN}Ticket Orbit-Platform{Styl.RESET}\n"
    #       f"{Styl.YELLOW}--------------------------------------------------{Styl.RESET}"
    #       )
    # for incident in sorted_incidents:
    #     if incident['service_offering']['name'] == 'Orbit-Platform':
    #         print(incident['number'], incident['priority'])

    # print(f"{Styl.GREEN}Ticket Orbit-Platform-Runtime{Styl.RESET}\n"
    #       f"{Styl.YELLOW}--------------------------------------------------{Styl.RESET}"
    #       )
    # for incident in sorted_incidents:
    #     if incident['service_offering']['name'] == 'Orbit-Platform-Runtime':
    #         print(incident['number'], incident['priority'])    