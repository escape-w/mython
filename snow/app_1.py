#!/usr/bin/env python3

import argparse
import os
import re
import json
from pathlib import Path
import requests
import pandas as pd
import warnings



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

    url = f"https://{SNOWUrl}.service-now.com/api/xyzag/v1/now_api/{ticket_type}"
    headers = {
        "Content-Type"  : "application/json",
        "Authorization" : f"id_token {token}"
    }
    
    response = requests.get(url, headers=headers)


    return response.json()

def format_value(value, width):
    return f"| {value:{width}} "

def structure_df(dataframe,col_mapping,type):
    print()
    print(" " * 50, type ,f"{Styl.GREEN} Summary {Styl.RESET}", " " * 50)
    print()
    dataframe.rename(columns=col_mapping, inplace=True)
    df = dataframe.copy()
    widths = df.applymap(lambda x: len(str(x))).max().tolist()
    column_widths = df.columns.map(len)
    widths = [max(cw, vw) for cw, vw in zip(column_widths, widths)]
    
    # Print column names
    print("|", end="")
    for col, width in zip(df.columns, widths):
        print(format_value(col, width), end="")
    print("|")
    
    # Print header separator
    print("|", end="")
    for width in widths:
        print("-" * (width + 4), end="")
    print("|")
    
    # Print DataFrame with formatted borders
    for index, row in df.iterrows():
        print("|", end="")
        for col, width in zip(row, widths):
            print(format_value(col, width), end="")
        print("|")
    
    # Print bottom border
    print("|", end="")
    for width in widths:
        print("-" * (width + 4), end="")
    print("|")
    print()

def inc_modify(df_inc):
    columns_to_fetch = ['number','priority','assignment_group.name','service_offering.name','caller_id.name','state','resolved_at']
    df_subset = df_inc[columns_to_fetch]
    column_names_mapping = {
    'assignment_group.name': 'Assignment Group',
    'service_offering.name': 'Service Offering',
    'caller_id.name': 'Caller Name'
    }
    structure_df(df_subset,column_names_mapping,"Incident")
    
def chg_modify(df_chg):
    columns_to_fetch = ['number','priority','assignment_group.name','service_offering.name','requested_by.name','risk']
    df_subset = df_chg[columns_to_fetch]
    column_names_mapping = {
    'assignment_group.name': 'Assignment Group',
    'service_offering.name': 'Service Offering',
    'requested_by.name': 'Requester Name'
    }
    structure_df(df_subset,column_names_mapping,"Change")

def pbi_modify(df_pbi):
    columns_to_fetch = ['number','priority','assignment_group','service_offering.name','state','business_service.name']
    df_subset = df_pbi[columns_to_fetch]
    column_names_mapping = {
    'assignment_group': 'Assignment Group',
    'service_offering.name': 'Service Offering',
    'caller_id.name': 'Caller Name'
    }
    structure_df(df_subset,column_names_mapping,"Problem")

if __name__ == "__main__":
    # Suppress all warnings
    warnings.filterwarnings("ignore")
    WORK_DIR=os.path.dirname(os.path.realpath(__file__))
    #args = parse_options()

    CONFIG_FILE = Path(WORK_DIR + "/config/.env.json")
    assert CONFIG_FILE.exists(), "config.json must present in config directory"

    config = json.load(open(CONFIG_FILE))
    
    token=get_token(config['AMBaseURL'],config['client_id'],config['client_secret'])

    inc_tickets = get_tickets(config['SNOWUrl'],token['access_token'],'incident')
    pbi_tickets = get_tickets(config['SNOWUrl'],token['access_token'],'problem')
    chg_tickets = get_tickets(config['SNOWUrl'],token['access_token'],'change_request')

    #print(inc_tickets)

    
    df_inc = pd.json_normalize(inc_tickets['result'])

    inc_modify(df_inc)
    df_chg = pd.json_normalize(chg_tickets['result'])
    chg_modify(df_chg)
    df_pbi = pd.json_normalize(pbi_tickets['result'])
    pbi_modify(df_pbi)
    
    #print(df_pbi.info())
    # Get maximum length of values in each column and column names to set width
    
          
    #print(sorted_incidents)
    #for incident in sorted_incidents:
    #    print(incident['number'], incident['priority'],incident['service_offering']['name'],incident['short_description'],incident['active'],incident['caller_id']['name'])
#
#
    #print(f"{Styl.GREEN}Ticket Orbit-Platform-CICD{Styl.RESET}\n"
    #      f"{Styl.YELLOW}--------------------------------------------------{Styl.RESET}"
    #      )
    #for incident in sorted_incidents:
    #    if incident['service_offering']['name'] == 'Orbit-Platform-CICD':
    #        print(incident['number'], incident['priority'])
    #
    #print(f"{Styl.GREEN}Ticket Orbit-Platform{Styl.RESET}\n"
    #      f"{Styl.YELLOW}--------------------------------------------------{Styl.RESET}"
    #      )
    #for incident in sorted_incidents:
    #    if incident['service_offering']['name'] == 'Orbit-Platform':
    #        print(incident['number'], incident['priority'])
#
    #print(f"{Styl.GREEN}Ticket Orbit-Platform-Runtime{Styl.RESET}\n"
    #      f"{Styl.YELLOW}--------------------------------------------------{Styl.RESET}"
    #      )
    #for incident in sorted_incidents:
    #    if incident['service_offering']['name'] == 'Orbit-Platform-Runtime':
    #        print(incident['number'], incident['priority'])    