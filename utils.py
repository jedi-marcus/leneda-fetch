#!/usr/bin/python3
import requests
import yaml
import curses
import os
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import pyfiglet
import json
import pytz
from pprint import pprint

def load_config():
    """Load configuration from config.yaml in the script directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.yaml')
    
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    return config

def select_pod(stdscr, pods):
    """Display and handle POD selection UI."""
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
    """Get list of last 12 months in format 'Month Year'."""
    # Use Luxembourg timezone
    lux_tz = pytz.timezone('Europe/Luxembourg')
    current_date = datetime.now(lux_tz)
    months = []

    for i in range(12):
        month_year = current_date.strftime("%B %Y")
        months.append(month_year)
        current_date -= timedelta(days=30)

    return months

def select_month(stdscr):
    """Display and handle month selection UI."""
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

def get_data(pod, month, config, save_raw=False):
    """Fetch data for a specific POD and month."""
    base_url = config.get('url', '')
    headers = config.get('headers', {})
    
    # Use Luxembourg timezone
    date_object = datetime.strptime(month, "%B %Y")
    # Set timezone to Europe/Luxembourg
    lux_tz = pytz.timezone('Europe/Luxembourg')
    date_object = lux_tz.localize(date_object)

    # get first and last day of month in format 2025-03-01T00:00:00Z but according to luxembourg timezone
    # Get first day of month at midnight in Luxembourg time
    first_day = date_object.replace(day=1, hour=0, minute=0, second=0)
    
    # Get last day of month at 23:59:59 in Luxembourg time
    last_day = (first_day + relativedelta(months=1) - timedelta(seconds=1))
    
    # Convert to UTC while preserving the local time
    first_day = first_day.astimezone(pytz.UTC)
    last_day = last_day.astimezone(pytz.UTC)

    first_day = first_day.strftime("%Y-%m-%dT%H:%M:%SZ")
    last_day = last_day.strftime("%Y-%m-%dT%H:%M:%SZ")

    url = base_url % (pod['id'])

    params = {
        'startDateTime': first_day,
        'endDateTime': last_day,
        'obisCode': '1-1:1.29.0'
    }

    response = requests.get(url, headers=headers, params=params)
    response_data = response.json()

    if save_raw:
        # Save raw JSON to file
        timestamp = datetime.now(lux_tz).strftime("%Y%m%d-%H%M%S")
        filename = f"{date_object.year}-{date_object.month:02d}-{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(response_data, f, indent=2)
        print(f"Saved data to {filename}")

    return response_data['items']

def display_user_header(user):
    """Display ASCII art header with user name."""
    ascii_art = pyfiglet.figlet_format(user)
    print(ascii_art, end='') 