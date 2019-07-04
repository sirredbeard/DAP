#!/usr/bin/env python3

# library dependencies

import sqlite3
from datetime import datetime

# app depedencies

import database

# functions

def screen():

    print ('screening cases for creditors/keywords')

    # read case information from NEWCASES

    # loop:

        # check if plaintiff_name contains any keywords in CREDITORS anywhere

        # if a match is found, move case from NEWCASES to POSSIBLECASES

        # if no match is found, move case from NEWCASES TO REJECTED CASES, give reason "UNKNOWN CREDITOR"

    return 0

# main program

def main():
    screen()
    return 0

main ()