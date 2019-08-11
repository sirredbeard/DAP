#!/usr/bin/env python3


# library dependencies
from datetime import datetime
import sqlite3


# app dependencies
import database
from api_interfaces import *
from api_keys import *


# functions
from database import db_get_matched_cases
from dap_logging import dap_log, LogType, LogLevel


def format_log_message(message_type, defendant_name, send_address, date):
    """
    Format message for logging to compliance.log
    """
    return "%s sent -- TO[%s] AT[%s] DATE[%s]" % (message_type, defendant_name, send_address, date)


def send_snailmail(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_street, defendant_city, defendant_state, defendant_zip):
    """
    Send snailmail via lob api, record date/time, write to compliance.log and return the date/time 
    """
    mail_results = api_lob(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_street, defendant_city, defendant_state, defendant_zip)
    dt = datetime.now()
    defendant_address = "%s, %s, %s, %s" % (defendant_street, defendant_city, defendant_state, defendant_zip)
    dap_log(log_type=LogType.COMPLIANCE, log_level=LogLevel.INFO, message=format_log_message("SNAILMAIL", defendant_name, defendant_address, dt))
    return dt


def send_email(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email):
    """
    Send email via clicksend api, record date/time, write to compliance.log and return the date/time
    """
    email_results = api_clicksend(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email)
    dt = datetime.now()
    dap_log(log_type=LogType.COMPLIANCE, log_level=LogLevel.INFO, message=format_log_message("EMAIL", defendant_name, defendant_email, dt))
    return dt


def send_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook):
    """
    Send message via facebook chat, record date/time, write to compliance.log and return the date/time
    """
    facebook_results = api_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook)
    dt = datetime.now()
    dap_log(log_type=LogType.COMPLIANCE, log_level=LogLevel.INFO, message=format_log_message("FACEBOOK", defendant_name, defendant_facebook, dt))
    return dt


def normalize(to_normalize):
    # ! convert variable passed from ALL CAPS to Normal Capitalization
    return to_normalize.title()


def process_matches():
    # ! to implement:

    matched_cases = db_get_matched_cases()
    for mc in matched_cases:
        if mc['DEFENDANT_STREET']:
            snailmail_timestamp = send_snailmail(mc['court_name'], mc['case_number'],
                                                 mc['date_filed'], normalize(mc['plaintiff_name']),
                                                 normalize(mc['defendant_name']),
                                                 normalize(mc['defendant_street']), normalize(mc['defendant_city']),
                                                 mc['defendant_state'],
                                                 mc['defendant_zip'])

    # if an e-mail address exists

    # normalize(plaintiff_name, defendant_name)

    # email_timestamp = send_email(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email)

    # if a facebook address exists

    # normalize(plaintiff_name, defendant_name)

    # facebook_timestamp = send_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook)

    # then move from MATCHEDCASES to PROCESSEDCASES, adding time-stamps for any/each of the above

    return 0


# main program

def main():
    process_matches()
    return 0


main()
