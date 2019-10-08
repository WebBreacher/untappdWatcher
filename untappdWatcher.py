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
import csv
from random import *
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sqlite3
from sqlite3 import Error
import sys
import time

# Parse command line input
parser = argparse.ArgumentParser(description='Grab Untappd user activity')
parser.add_argument('-b', '--bar', help='Export entries about a single bar. Ex: "Westside Massive"')
parser.add_argument('-d', '--date', help='Export entries about a single date. Ex: "04 Sep 2019"')
parser.add_argument('-e', '--export', action='store_true', help='Export all records from DB to CSV')
parser.add_argument('-l', '--location', help='Export entries about a single location. Ex: "Newark, NJ"')
parser.add_argument('-n', '--new', action='store_true', help='Only show new entries')
parser.add_argument('-t', '--time', help='Export entries about a single time. Ex: "14:09"')
parser.add_argument('-u', '--user', help='Export entries about a single user. Ex: johndoe121')
args = parser.parse_args()

####
# Functions
####

def extract_bars():
    bars = []
    try:
        infile = open('target_bars.txt','r')
        for line in infile:
            matchObj = re.match( r'^https\://untappd\.com/.*', line)
            if matchObj:
                bars.append(line.strip())
    except Error as e:
        print('[ !!! ] Error! Cannot read the target_bars.txt file.')
        sys.exit()
    finally:
        infile.close()

    return bars

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print('[ !!! ] Error! Cannot connect to DB - {}'.format(e))
        sys.exit()
    return conn

def create_table(conn, db_file):
    create_table_sql = """CREATE TABLE IF NOT EXISTS watcher (
                                    barname TEXT NOT NULL,
                                    barlocation TEXT NOT NULL,
                                    username TEXT NOT NULL,
                                    postdate TEXT NOT NULL,
                                    posttime TEXT NOT NULL);"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print('[ !!! ] Error! Cannot create table - {}'.format(e))
        sys.exit(1)

def insert_bar_data(conn, bar_data):
    sql = ''' INSERT INTO watcher(barname,barlocation,username,postdate,posttime) VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, bar_data)
    return cur.lastrowid

def search_for_bar_data(conn, bar_data):
    sql = ''' SELECT * FROM watcher WHERE barname=? AND barlocation=? AND username=? AND postdate=? and posttime=? '''
    cur = conn.cursor()
    cur.execute(sql, bar_data)
    rows = cur.fetchall()
    if rows:
        if not args.new:
            print('[ - ] Found {}.'.format(rows))
    else:
        print("[ + ] Inserting {}.".format(bar_data))
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
        print('[ !!! ]   ERROR - Untappd issue: {}'.format(str(e)))
        sys.exit(1)

def get_bar_data(conn, db_file, passed_bar):
    # Parsing bar information
    print("[   ] Requesting {}".format(passed_bar))
    resp = get_data_from_untappd(passed_bar)
    html_doc = BeautifulSoup(resp, 'html.parser')
    bar1 = html_doc.find_all('a', 'time timezoner track-click')
    barnameloc = html_doc.title.string.split(' - ')

    with conn:
        if bar1:
            for bar in bar1:
                matchuserobj = re.findall(r'user/(.+)/checkin/.*?">[A-Z][a-z][a-z], ([0-9][0-9] [A-Z][a-z][a-z] [12][0-9]{3}) ([0-2][0-9]:[0-5][0-9]:[0-5][0-9]) \+0000</a>', str(bar), re.DOTALL)
                if matchuserobj:
                    for user in matchuserobj:
                        bar_data = (barnameloc[0], barnameloc[1],user[0], user[1], user[2])
                        search_for_bar_data(conn, bar_data)

def export_db(conn, part, param):
    timestr = time.strftime('%Y%m%d-%H%M%S')
    outfile = 'output-{}-{}.csv'.format(part, timestr)

    if part == 'date':
        sql = "SELECT * FROM watcher WHERE postdate like '%{}%'".format(param)
    elif part == 'time':
        sql = "SELECT * FROM watcher WHERE posttime like '%{}%'".format(param)
    elif part == 'barname':
        sql = "SELECT * FROM watcher WHERE barname like '%{}%'".format(param)
    elif part == 'location':
        sql = "SELECT * FROM watcher WHERE barlocation like '%{}%'".format(param)
    elif part == 'user':
        sql = "SELECT * FROM watcher WHERE username like '%{}%'".format(param)
    else:
        sql = ''' SELECT * FROM watcher '''

    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    if rows:
        print('[ + ] Exporting to file: {}'.format(outfile))
        with open(outfile, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Bar Name","Bar Location", "User Name", "Post Date", "Post Time"])
            writer.writerows(rows)
        print('[ + ] Exported the following rows to CSV')
        for row in rows:
            print('         {}'.format(row))

###########################
# Start
###########################

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Check input bar file and extract bars
bars = extract_bars()

# Set up the connection to the database
db_file = r'untappdWatcher.sqlite3'
conn = create_connection(db_file)

# Check for/create DB table
create_table(conn, db_file)

if args.export or args.date or args.location or args.time or args.user or args.bar:
    part = 'full'
    param = ''

    if args.date:
        part = 'date'
        param = args.date
    elif args.time:
        part = 'time'
        param = args.time
    elif args.user:
        part = 'user'
        param = args.user
    elif args.bar:
        part = 'barname'
        param = args.bar
    elif args.location:
        part = 'location'
        param = args.location

    export_db(conn, part, param)
    exit()

# Get bar info
for bar in bars:
    get_bar_data(conn, db_file, bar)
    time.sleep(uniform(1,9)) # Pause 2-8 seconds between requests to not get banned