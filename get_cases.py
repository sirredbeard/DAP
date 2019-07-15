#!/usr/bin/env python3

# library dependencies

import random
from datetime import datetime
from py3270 import Emulator

# app depedencies

from mainframe_credentials import MainframeIP, MainframeUsername, MainframePassword
from mainframe import *
from database import *


# functions

def scan(court_name, last_successful_case_number):
    mainframe_open_connection()  # opens connection to mainframe
    mainframe_login()  # performs login routines
    mainframe_check_login_worked()  # double-check to make sure we are logged in

    case_number_to_search = last_successful_case_number

    while case_number_to_search < last_successful_case_number + 35:

        mainframe_select_CATS()  # enter the CATS function on the mainframe
        mainframe_open_docket_search()  # open the docket search page
        mainframe_search_case(court_name, case_number_to_search)  # enter our docket search information
        case_exists = mainframe_check_case_exists()  # see what the server returned from our search

        if case_exists == 0:
            judge_name, date_filed, time_filed, plaintiff_name, defendant_name = mainframe_parse_case()  # continue and pull the data from mainframe
            db_write_new_case(court_name, case_number_to_search, judge_name, date_filed, time_filed, plaintiff_name,
                              defendant_name)  # write data to NEWCASES
            mainframe_reset()
            return case_number_to_search

        if case_exists == 1:
            case_number_to_search += 1

    return last_successful_case_number  # send this back


def each_court(court_name):
    # this function sets up our scan by getting the last succesfully verified case number on record for each court
    # we are about to scan, launch the scan with that number, and then store the last successfully accessed case number from this scan
    last_successful_case_number = db_get_latest_case_number(
        court_name)  # the get last known case from the database from CASENUMBERS for court_name
    last_successful_case_number = scan(court_name,
                                       last_successful_case_number)  # scan, giving back last known successfully accessed case number
    db_write_latest_case_number(court_name,
                                last_successful_case_number)  # write the last known successfully access case number back to CASENUMBERS
    return 0


def get_superior_court():  # this function defines superior court as the court we will be searching and then moves on to set up our scan
    print('getting superior court cases')
    court_name = "SU"  # stands for superior court
    each_court(court_name)
    return 0


def get_state_court():
    print('getting state court cases')
    court_name = "SC"  # stands for state court
    each_court(court_name) 
    return 0


def get_magistrate_court():
    print('getting magistrate court cases')
    court_name = "MG"  # stands for magistrate court
    each_court(court_name)
    return 0


def get_municipal_court():
    print('getting municipal court cases')
    court_name = "MC"  # stands for municipal court
    each_court(court_name)
    return 0


# main function

def main():
    get_superior_court()  # scan for new cases in each court, starting with superior court
    get_state_court()
    get_magistrate_court()
    get_municipal_court()


main()

# ! log that this was run on this date/time to compliance.log
