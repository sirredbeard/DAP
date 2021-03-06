#!/usr/bin/env python3

# library dependencies

import random
from datetime import datetime
from py3270 import Emulator

# app depedencies

from mainframe_credentials import MainframeIP, MainframeUsername, MainframePassword
from mainframe import *
from database import *
from dap_logging import dap_log_general, LogLevel

# functions

def scan(court_name, last_successful_case_number):
    dap_log_general(LogLevel.DEBUG, "scan for cases")

    mainframe_open_connection()  # opens connection to mainframe
    mainframe_login()  # performs login routines
    mainframe_check_login_worked()  # double-check to make sure we are logged in

    case_number_to_search = last_successful_case_number + 1
    no_case_count = 0

    while no_case_count < 35:

        mainframe_select_CATS()  # enter the CATS function on the mainframe
        mainframe_open_docket_search()  # open the docket search page
        mainframe_search_case(court_name, case_number_to_search)  # enter our docket search information
        case_exists = mainframe_check_case_exists()  # see what the server returned from our search

        if case_exists == 1:
            year, judge_name, date_filed, time_filed, plaintiff_name, plaintiff_counsel, defendant_name, defendant_counsel, civil_action, action_description = mainframe_parse_case()  # pull the data from mainframe

            dap_log_general(LogLevel.DEBUG, "checking data")

            if plaintiff_name == "ERROR" or defendant_name == "ERROR":
                dap_log_general(LogLevel.ERROR, "error detected in data, gracefully ending session")
                no_case_count = 35
            else:
                dap_log_general(LogLevel.INFO, "writing case to NEW_CASE")
                db_write_new_case(court_name, last_successful_case_number, year, judge_name, date_filed, time_filed, plaintiff_name, plaintiff_counsel, defendant_name, defendant_counsel, civil_action, action_description)  # write data to NEW_CASE
                last_successful_case_number = case_number_to_search
                case_number_to_search += 1
                dap_log_general(LogLevel.INFO, "resetting error counter")
                no_case_count = 0
                mainframe_reset()
        else:
            dap_log_general(LogLevel.INFO, "error counter: %i" % no_case_count)
            case_number_to_search += 1
            no_case_count += 1
            mainframe_reset()

    return last_successful_case_number  # send this back


def each_court(court_name):
    # this function sets up our scan by getting the last succesfully verified case number on record for each court
    # we are about to scan, launch the scan with that number, and then store the last successfully accessed case number from this scan
    last_successful_case_number = db_get_latest_case_number(
        court_name)  # the get last known case from the database from CASENUMBERS for court_name
    last_successful_case_number = scan(court_name,
                                       last_successful_case_number)  # scan, giving back last known successfully accessed case number
    mainframe_close_connection()
    db_write_latest_case_number(court_name,
                                last_successful_case_number)  # write the last known successfully access case number back to CASENUMBERS
    return 0


def get_superior_court():  # this function defines superior court as the court we will be searching and then moves on to set up our scan
    dap_log_general(LogLevel.DEBUG, "getting superior court cases")
    court_name = "SU"  # stands for superior court
    each_court(court_name)
    return 0


def get_state_court():
    dap_log_general(LogLevel.DEBUG, "getting state court cases")
    court_name = "SC"  # stands for state court
    each_court(court_name) 
    return 0


def get_magistrate_court():
    dap_log_general(LogLevel.DEBUG, "getting magistrate court cases")
    court_name = "MG"  # stands for magistrate court
    each_court(court_name)
    return 0


def get_municipal_court():
    dap_log_general(LogLevel.DEBUG, "getting municipal court cases")
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
