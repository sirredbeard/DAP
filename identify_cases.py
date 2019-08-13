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
    print("identify")

    # read case information from POSSIBLE_CASE
    possible_cases = db_get_possible_cases()

    print ("loaded possible cases")

    for possible_case in possible_cases:

        # perform lookup against pipl api:

        defendant = api_pipl(possible_case[1])

        print(defendant)

        if defendant['match_true']:
            print('pipl match found')

            database.db_move_to_matched_cases(possible_case[0], defendant["house"], defendant["street"], defendant["apartment"], defendant["city"], defendant["zip"], defendant["email"], defendant["facebook"])
        
        else:
            print('pipl match not found')
            # move from POSSIBLE_CASE to REJECTEDCASES, reason "UNABLE TO ID"

            database.db_move_to_unmatched_cases(possible_case[0])

    return 0


# main program

def main():
    print("main")
    identify()
    return 0


main()

# ! log that this was run on this date/time to compliance.log
