#!/usr/bin/env python3

# library dependencies

import sqlite3
from datetime import datetime

# app dependencies

import database
from database import db_get_possible_cases
from api_interfaces import api_pipl


# functions

def identify():
    # read case information from POSSIBLE_CASE
    possible_cases = db_get_possible_cases()

    for possible_case in possible_cases:

        # perform lookup against pipl api:

        defendant = api_pipl(possible_case[1])

        if defendant['match_true']:
            print('pipl match found')
            database.db_move_to_matched_cases(possible_case[0], defendant["house"], defendant["street"], 
                                            defendant["apt"], defendant["city"], defendant["zip"], defendant["email"],
                                            defendant["facebook"])
        else:
            print('pipl match not found')
            # move from POSSIBLE_CASE to REJECTEDCASES, reason "UNABLE TO ID"

    return 0


# main program

def main():
    identify()
    return 0


main()

# ! log that this was run on this date/time to compliance.log
