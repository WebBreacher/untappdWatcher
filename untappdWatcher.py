#!/usr/bin/python
"""
    Author: Micah Hoffman (@WebBreacher)
    Purpose: To look up a bar/pub/brewery on Untappd.com and watch who drinks there
    Inspired by Ryan in my SEC487 class!
"""

import argparse
from bs4 import BeautifulSoup
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sqlite3
import sys


####
# Functions
####

# Parse command line input
'''parser = argparse.ArgumentParser(description='Grab Untappd user activity')
parser.add_argument('-b', '--bar', required=True, help='Bar/pub/brewery to research')
args = parser.parse_args()'''

def database_check():
    # Check if a DB exists and is in the correct format
    # If not, create one
    try:
        fh = open('untappdWatcher.sqlite3', 'a')
    except:
        print('[!!!] ERROR. Cannot open the untappdWatcher.db file for appending. Ensure the file exists and is writable by the script.')
        sys.exit(1)
    else:
        print("[+] DB found and can be opened for appending")
        fh.close()
        # Try to connect to the DB
        conn = sqlite3.connect('untappdWatcher.sqlite3')
        print("[+] UntappdWatcher DB opened successfully")


def get_data_from_untappd(url):
    # Setting up and Making the Web Call
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/69.0'
        headers = {'User-Agent': user_agent}
        # Make web request for that URL and don't verify SSL/TLS certs
        response = requests.get(url, headers=headers, verify=False)
        return response.text

    except Exception as e:
        print('[!]   ERROR - Untappd issue: {}'.format(str(e)))
        exit(1)


def get_bar_data(passed_bar):
    # Parsing bar information
    print("\n[ ] Requesting {}".format(passed_bar))
    resp = get_data_from_untappd(passed_bar)
    html_doc = BeautifulSoup(resp, 'html.parser')
    bar1 = html_doc.find_all('a', 'time timezoner track-click')
    bar_name = html_doc.title.string.strip(' - Untappd')
    
    print(bar_name)

    if bar1:
        return bar1

###########################
# Start
###########################

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Check for DB
database_check()

###############
# Get bar info
###############
#bar = get_bar_data('https://untappd.com/v/81bay-brewing-co/4883588')
bar = get_bar_data('https://untappd.com/v/ford-s-garage/3103119')
#bar = get_bar_data('https://untappd.com/v/4-creeks-brewhouse/8829089')

for bar1 in bar:
    matchuserobj = re.findall('user/(.+)/checkin/.*?">(.+)</a>', str(bar1), re.DOTALL)
    if matchuserobj:
        for user in matchuserobj:
            place = '{}, {}'.format(user[0],user[1])
            print(place)

# Open SQliteDB

# Check to see if there already is an entry for what we have

# if not, add it to the DB
