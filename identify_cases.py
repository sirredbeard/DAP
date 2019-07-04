#!/usr/bin/env python3

# library dependencies

import sqlite3
from datetime import datetime

# app depedencies

import database
import api_interfaces

# functions

def identify():

    # read case information from POSSIBLECASES

    # loop:

        # perform lookup against plpl api:

        match_true, defendant_street, defendant_city, defendant_zip, defendant_email, defendant_facebook = api_plpl(defendant_name)

        if match_true == true:
            print('plpl match found')
            # move case to MATCHEDCASES with additional information

        if match_true == false:
            print('plpl match not found')
            # move from POSSIBLECASES to REJECTEDCASES, reason "UNABLE TO ID" 

    return 0

# main program

def main():
    identify()
    return 0

main ()