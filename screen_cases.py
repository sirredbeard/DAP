#!/usr/bin/env python3

# library dependencies

import sqlite3
from datetime import datetime

# app depedencies

import database


# functions

def screen():
    print('screening cases for creditors/keywords')

    database.db_screen_cases()

    return 0


# main program

def main():
    screen()
    return 0


main()

# ! log that this was run on this date/time to compliance.log
