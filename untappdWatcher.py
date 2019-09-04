#!/usr/bin/python
"""
    Author: Micah Hoffman (@WebBreacher)
    Purpose: To look up a bar/pub/brewery on Untappd.com and watch who drinks there
    Inspired by Ryan in my SEC487 class!
    https://github.com/WebBreacher/untappdWatcher

    Huge thanks to https://www.sqlitetutorial.net/sqlite-python/insert/ for the sqlite python help
"""

import argparse
from bs4 import BeautifulSoup
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sqlite3
from sqlite3 import Error
import sys

####
# Functions
####

# Parse command line input
'''parser = argparse.ArgumentParser(description='Grab Untappd user activity')
parser.add_argument('-b', '--bar', required=True, help='Bar/pub/brewery to research')
args = parser.parse_args()'''

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print('[!!!] Error! Cannot connect to DB - {}'.format(e))
        sys.exit()

    return conn

def create_table(conn, db_file):
    create_table_sql = """CREATE TABLE IF NOT EXISTS watcher (
                                    barname TEXT NOT NULL,
                                    username TEXT NOT NULL,
                                    postdate TEXT NOT NULL);"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print('[!!!] Error! Cannot create table - {}'.format(e))
        sys.exit(1)

def insert_bar_data(conn, bar_data):
    sql = ''' INSERT INTO watcher(barname,username,postdate) VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, bar_data)
    return cur.lastrowid

def search_for_bar_data(conn, bar_data):
    sql = ''' SELECT * FROM watcher WHERE barname=? AND username=? AND postdate=? '''
    cur = conn.cursor()
    cur.execute(sql, bar_data)
    rows = cur.fetchall()
    if rows:
        print('[-] Found {}.'.format(rows))
    else:
        print("[+] Inserting {}.".format(bar_data))
        insert_bar_data(conn, bar_data)

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

def get_bar_data(conn, db_file, passed_bar):
    # Parsing bar information
    print("\n[ ] Requesting {}".format(passed_bar))
    resp = get_data_from_untappd(passed_bar)
    html_doc = BeautifulSoup(resp, 'html.parser')
    bar1 = html_doc.find_all('a', 'time timezoner track-click')
    barname = html_doc.title.string.strip(' - Untappd')

    with conn:
        if bar1:
            for bar in bar1:
                matchuserobj = re.findall('user/(.+)/checkin/.*?">(.+)</a>', str(bar), re.DOTALL)
                if matchuserobj:
                    for user in matchuserobj:
                        #place = '{}, {}'.format(user[0],user[1])
                        bar_data = (barname, user[0], user[1])
                        search_for_bar_data(conn, bar_data)

###########################
# Start
###########################

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set up the connection to the database
db_file = r'untappdWatcher.sqlite3'
conn = create_connection(db_file)

# Check for DB table
create_table(conn, db_file)

# Get bar info
bar = get_bar_data(conn, db_file, 'https://untappd.com/v/81bay-brewing-co/4883588')
bar = get_bar_data(conn, db_file, 'https://untappd.com/v/ford-s-garage/3103119')
bar = get_bar_data(conn, db_file, 'https://untappd.com/v/4-creeks-brewhouse/8829089')

