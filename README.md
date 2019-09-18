# untappdWatcher

A student named "Ryan" in my [SEC487 class](https://sans.org/sec487) saw the [UntappdScraper project](https://github.com/webbreacher/untappdscraper) I made and wondered if we could shift the focus of the tool to watch a bar/pub and see who logs in there over time instead of watching users. I thought that might be a cool shift for this project so I made this!

The goal of this OSINT tool is to, given a specific bar or pub:

* Retrieve who logs untappd.com drinks there
* Retrieve when those people logged the drinks (shows possible times they were there)
* Track these logged drinks over time
* Retrieve user behaviors/patterns of life from the results
  * How often people visit a place
  * Are there patterns when people visit (Monday, Wednesday, Friday after work?)

The output from this is going to be a CSV for now since further analysis can easily be performed in Excel or another spreadsheet app.

## Caveats

Since this script scrapes the public pages:
* Private Untappd profiles are may not be scraped

## Usage

### Requirements

The most important requirement is __Python 3.x__.

#### Modules

* bs4
* requests

If you have PIP installed, type: `pip3 install -r requirements.txt` from the command line and your system should install all required modules.

## Help command Output

```bash
$ python3 untappdWatcher.py -h
usage: untappdWatcher.py [-h] [-b BAR] [-d DATE] [-e] [-l LOCATION] [-n]
                         [-t TIME] [-u USER]

Grab Untappd user activity

optional arguments:
  -h, --help            show this help message and exit
  -b BAR, --bar BAR     Export entries about a single bar. Ex: "Westside
                        Massive"
  -d DATE, --date DATE  Export entries about a single date. Ex: "04 Sep 2019"
  -e, --export          Export all records from DB to CSV
  -l LOCATION, --location LOCATION
                        Export entries about a single location. Ex: "Newark,
                        NJ"
  -n, --new             Only show new entries
  -t TIME, --time TIME  Export entries about a single time. Ex: "14:09"
  -u USER, --user USER  Export entries about a single user. Ex: johndoe121
```

## Example Output

```bash
$ python untappdWatcher.py


XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

```

## To Do

* 

## License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
