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

    return response_data['items']


def processData(items,threshold,month):

    threshold = threshold/4
    total_over = 0
    total = 0

    daily = {}
    daily_over = {}
    count = {}

    for item in items:

        total += (item['value']/4)

        date = item['startedAt'].split('T')[0]

        # if daily[date] is not defined, set it to 0
        if not daily.get(date):
            daily[date] = 0
            count[date] = 0

        daily[date] += (item['value']/4)
        count[date] += 1

        if (item['value']/4) > threshold:
            # output startedAt and value on a single line, nicely formatted

            if not daily_over.get(date):
                daily_over[date] = 0

            daily_over[date] += (item['value']/4) - threshold

    for day in daily:

        if daily_over.get(day):
            print(f"{count[day]:d} {day} - {daily[day]:.2f}  +{daily_over[day]:.2f}")
        else:
            print(f"{count[day]:d} {day} - {daily[day]:.2f}")

    total = 0
    total_over = 0

    # calculate total over threshold
    for day in daily_over:
        total_over += daily_over[day]

    # calculate total over threshold
    for day in daily:
        total += daily[day]
    

    # # price for over threshold
    price = total_over * 0.1139

    if total_over > 0:
        print('-' * 38)
        print(f"{'Total over threshold:':<25} {total_over:>8.2f} kWh")
        print(f"{'Price for over threshold:':<25} {price:>8.2f} €")

    total_price = calculate_price(total,pod['threshold'])


    # figure out number of days in month
    date_object = datetime.strptime(month, "%B %Y")

    days = calendar.monthrange(date_object.year, date_object.month)[1]

    # count items in daily
    count_items = len(daily.values())

    print('-' * 38)

    if count_items < days:

        # current total
        print(f"{'Current Total kWh:':<25} {total:>8.2f} kWh")
        print(f"{'Current Total price:':<25} {(total_price+price)*1.08:>8.2f} €")

        # estimate monthly price
        monthly_price = calculate_price(total/count_items*days,pod['threshold'])
        print(f"{'Estimated monthly kWh:':<25} {total/count_items*days:>8.2f} kWh")
        print(f"{'Estimated monthly price:':<25} {(monthly_price+price)*1.08:>8.2f} €")
    else:
        print(f"{'Total:':<25} {total:>8.2f} kWh")
        print(f"{'Total price:':<25} {(total_price+price)*1.08:>8.2f} €")

def calculate_price(kwh,threshold):

    # variable costs
    variable_costs = 0.15 + 0.0759 -0.0376 + 0.0010

    kwh_price = variable_costs * kwh

    # get price for threshold
    tprice = threshold_price.get(threshold,0)

    # fix costs
    fix_costs = 1.5 + 5.9 + tprice

    return fix_costs + kwh_price



pod = curses.wrapper(main)
month = curses.wrapper(select_month)

user = pod['name']

# Generate and display ASCII art of the user name
ascii_art = pyfiglet.figlet_format(user)
print(ascii_art, end='')

data = getData(pod,month)

processData(data,pod['threshold'],month)
