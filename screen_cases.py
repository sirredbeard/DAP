#!/usr/bin/env python3

# library dependencies

import sqlite3
from datetime import datetime

# app depedencies

import database
from dap_logging import dap_log_general, LogLevel

# functions

def screen():
    dap_log_general(LogLevel.DEBUG, "screening cases for creditors/keywords")

    database.db_screen_cases()

    return 0


# main program

def main():
    screen()
    return 0


main()

# ! log that this was run on this date/time to compliance.log
