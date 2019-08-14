#!/usr/bin/env python3

# library dependencies

import sqlite3
from datetime import datetime

# app dependencies

import database
from database import db_get_possible_cases
from api_interfaces import api_pipl
from dap_logging import dap_log_general, LogLevel

# functions

def identify():
    dap_log_general(LogLevel.DEBUG, "identifying cases...")

    # read case information from POSSIBLE_CASE
    possible_cases = db_get_possible_cases()
    dap_log_general(LogLevel.DEBUG, "loaded possible cases")

    for possible_case in possible_cases:

        # perform lookup against pipl api:

        defendant = api_pipl(possible_case[1])

        dap_log_general(LogLevel.DEBUG, str(defendant))

        if defendant['match_true']:
            dap_log_general(LogLevel.INFO, "pipl match found for: %s" % possible_case[1])

            database.db_move_to_matched_cases(possible_case[0], defendant["house"], defendant["street"], defendant["apartment"], defendant["city"], defendant["zip"], defendant["email"], defendant["facebook"])
        
        else:
            dap_log_general(LogLevel.INFO, "no pipl match for: %s" % possible_case[1])
            # move from POSSIBLE_CASE to REJECTEDCASES, reason "UNABLE TO ID"

            database.db_move_to_unmatched_cases(possible_case[0])

    return 0


# main program

def main():
    identify()
    return 0


main()

# ! log that this was run on this date/time to compliance.log
