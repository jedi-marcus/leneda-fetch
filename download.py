#!/usr/bin/python3
import requests
from pprint import pprint
import yaml
import sys
import curses
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import pyfiglet
import json
# Load configuration from config.yaml
with open('/home/jedi/work/20250221.leneda/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Load and display PODs from config
pods = config.get('PODs', [])
threshold_price = config.get('threshold_price', [])

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    current_row = 0

    while True:
        stdscr.clear()
        for idx, pod in enumerate(pods):
            x = 0
            y = idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, pod['name']+' '+pod['id'])
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, pod['name']+' '+pod['id'])
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(pods) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            break

    selected_pod = pods[current_row]
    stdscr.clear()

    return selected_pod

def get_month_year():
    current_date = datetime.now()
    months = []

    for i in range(12):
        month_year = current_date.strftime("%B %Y")
        months.append(month_year)
        current_date -= timedelta(days=30)

    return months

def select_month(stdscr):

    months = get_month_year()
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    current_row = 0

    while True:
        stdscr.clear()
        for idx, month in enumerate(months):
            x = 0
            y = idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, month)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, month)
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(months) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            break

    selected_month = months[current_row]
    stdscr.clear()

    return selected_month

def getData(pod,month):

    base_url = config.get('url', '')
    headers = config.get('headers', {})
    date_object = datetime.strptime(month, "%B %Y")

    # get first and last day of month in format 2025-03-01T00:00:00Z
    first_day = date_object.strftime("%Y-%m-%dT%H:%M:%SZ")

    # get last day of month
    last_day = (date_object + relativedelta(months=1) - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = base_url % (pod['id'])

    params = {
        'startDateTime': first_day,
        'endDateTime': last_day,
        'obisCode': '1-1:1.29.0'
    }

    response = requests.get(url, headers=headers, params=params)
    response_data = response.json()

    # Save raw JSON to file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{date_object.year}-{date_object.month:02d}-{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(response_data, f, indent=2)
    
    print(f"Saved data to {filename}")

pod = curses.wrapper(main)
month = curses.wrapper(select_month)

user = pod['name']

# Generate and display ASCII art of the user name
ascii_art = pyfiglet.figlet_format(user)
print(ascii_art, end='')

data = getData(pod,month)

