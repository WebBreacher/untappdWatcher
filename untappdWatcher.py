#!/usr/bin/python
"""
    Author: Micah Hoffman (@WebBreacher)
    Purpose: To look up a bar/pub/brewery on Untappd.com and watch who drinks there
    Inspired by Ryan in my SEC487 class!
    https://github.com/WebBreacher/untappdWatcher
"""

import argparse
from bs4 import BeautifulSoup
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sqlite3
from sqlite3 import Error
import sys

db_file = 'untappdWatcher.sqlite3'


####
# Functions
####

# Parse command line input
'''parser = argparse.ArgumentParser(description='Grab Untappd user activity')
parser.add_argument('-b', '--bar', required=True, help='Bar/pub/brewery to research')
args = parser.parse_args()'''

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    From https://www.sqlitetutorial.net/sqlite-python/create-tables/
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print('[!!!] Error! Cannot connect to DB - {}'.format(e))
        sys.exit()
 
    return conn

def create_table():
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    From https://www.sqlitetutorial.net/sqlite-python/create-tables/
    """
    create_table_sql = """CREATE TABLE IF NOT EXISTS watcher (
                                    id INT PRIMARY KEY NOT NULL,
                                    barname TEXT NOT NULL,
                                    username TEXT NOT NULL,
                                    postdate TEXT NOT NULL);"""
    try:
        conn = create_connection(db_file)
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print('[!!!] Error! Cannot create table - {}'.format(e))
        sys.exit(1)

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
        sys.exit(1)


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

# Check for DB table
create_table()


###############
# Get bar info
###############
#bar = get_bar_data('https://untappd.com/v/81bay-brewing-co/4883588')
'''bar = get_bar_data('https://untappd.com/v/ford-s-garage/3103119')
#bar = get_bar_data('https://untappd.com/v/4-creeks-brewhouse/8829089')

for bar1 in bar:
    matchuserobj = re.findall('user/(.+)/checkin/.*?">(.+)</a>', str(bar1), re.DOTALL)
    if matchuserobj:
        for user in matchuserobj:
            place = '{}, {}'.format(user[0],user[1])
            print(place)
'''


# Check to see if there already is an entry for what we have

# if not, add it to the DB
