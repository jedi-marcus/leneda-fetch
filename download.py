#!/usr/bin/python3
import curses
from utils import (
    load_config,
    select_pod,
    select_month,
    get_data,
    display_user_header
)

# Load configuration
config = load_config()
pods = config.get('PODs', [])

def main(stdscr):
    return select_pod(stdscr, pods)

# Main execution
pod = curses.wrapper(main)
month = curses.wrapper(select_month)
user = pod['name']

display_user_header(user)
get_data(pod, month, config, save_raw=True)

