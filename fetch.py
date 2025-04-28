#!/usr/bin/python3
import curses
from utils import (
    load_config,
    select_pod,
    select_month,
    get_data,
    display_user_header
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import pyfiglet
import json
import os
import pytz

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.yaml')

# Load configuration
config = load_config()
pods = config.get('PODs', [])
threshold_price = config.get('threshold_price', [])

def processData(items, threshold, month):
    threshold = threshold/4
    total_over = 0
    total = 0

    daily = {}
    daily_over = {}
    count = {}

    for item in items:
        total += (item['value']/4)

        # Convert UTC timestamp to Luxembourg time
        utc_time = datetime.strptime(item['startedAt'], "%Y-%m-%dT%H:%M:%SZ")
        utc_time = utc_time.replace(tzinfo=pytz.UTC)
        lux_time = utc_time.astimezone(pytz.timezone('Europe/Luxembourg'))
        item['startedAt'] = lux_time.strftime("%Y-%m-%dT%H:%M:%S")
        date = item['startedAt'].split('T')[0]

        if not daily.get(date):
            daily[date] = 0
            count[date] = 0

        daily[date] += (item['value']/4)
        count[date] += 1

        if (item['value']/4) > threshold:
            if not daily_over.get(date):
                daily_over[date] = 0
            daily_over[date] += (item['value']/4) - threshold

    for day in daily:
        if daily_over.get(day):
            print(f"{count[day]:>3d} {day} - {daily[day]:>6.3f}  +{daily_over[day]:.3f}")
        else:
            print(f"{count[day]:>3d} {day} - {daily[day]:>6.3f}")

    total = 0
    total_over = 0

    for day in daily_over:
        total_over += daily_over[day]

    for day in daily:
        total += daily[day]

    price = total_over * 0.1139

    if total_over > 0:
        print('-' * 38)
        print(f"{'Total over threshold:':<25} {total_over:>8.2f} kWh")
        print(f"{'Price for over threshold:':<25} {price:>8.2f} €")

    total_price = calculate_price(total, pod['threshold'])

    date_object = datetime.strptime(month, "%B %Y")
    days = calendar.monthrange(date_object.year, date_object.month)[1]
    count_items = len(daily.values())

    print('-' * 38)

    if count_items < days:
        print(f"{'Current Total kWh:':<25} {total:>8.2f} kWh")
        print(f"{'Current Total price:':<25} {(total_price+price)*1.08:>8.2f} €")
        monthly_price = calculate_price(total/count_items*days, pod['threshold'])
        print(f"{'Estimated monthly kWh:':<25} {total/count_items*days:>8.2f} kWh")
        print(f"{'Estimated monthly price:':<25} {(monthly_price+price)*1.08:>8.2f} €")
    else:
        print(f"{'Total:':<25} {total:>8.2f} kWh")
        print(f"{'Total price:':<25} {(total_price+price)*1.08:>8.2f} €")

def calculate_price(kwh, threshold):
    variable_costs = 0.15 + 0.0759 -0.0376 + 0.0010
    kwh_price = variable_costs * kwh
    tprice = threshold_price.get(threshold, 0)
    fix_costs = 1.5 + 5.9 + tprice
    return fix_costs + kwh_price

def main(stdscr):
    return select_pod(stdscr, pods)

# Main execution
pod = curses.wrapper(main)
month = curses.wrapper(select_month)
user = pod['name']

display_user_header(user)
data = get_data(pod, month, config)
processData(data, pod['threshold'], month)
