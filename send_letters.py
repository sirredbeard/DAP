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
from dap_logging import dap_log_compliance, LogLevel


def format_log_message(message_type, defendant_name, send_address, date):
    """
    Format message for logging to compliance.log
    """
    return "%s sent -- TO[%s] AT[%s] DATE[%s]" % (message_type, defendant_name, send_address, date)


def send_snailmail(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_house, defendant_street, defendant_apt, defendant_city, defendant_state, defendant_zip):
    """
    Send snailmail via lob api, record date/time, write to compliance.log and return the date/time 
    """
    mail_results = api_lob(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_house, defendant_street, defendant_apt, defendant_city, defendant_state, defendant_zip)
    dt = datetime.now()

    if defendant_apt == "":
        defendant_address = "%s %s, %s, %s, %s" % (defendant_house, defendant_street, defendant_city, defendant_state, defendant_zip)
    else:
        defendant_address = "%s %s APT %s, %s, %s %s" % (defendant_house, defendant_street, defendant_apt, defendant_city, defendant_state, defendant_zip)
    
    dap_log_compliance(LogLevel.INFO, format_log_message("SNAILMAIL", defendant_name, defendant_address, dt))
    return dt


def send_email(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email):
    """
    Send email via clicksend api, record date/time, write to compliance.log and return the date/time
    """
    email_results = api_clicksend(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email)
    dt = datetime.now()
    dap_log_compliance(LogLevel.INFO, format_log_message("EMAIL", defendant_name, defendant_email, dt))
    return dt


def send_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook):
    """
    Send message via facebook chat, record date/time, write to compliance.log and return the date/time
    """
    facebook_results = api_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook)
    dt = datetime.now()
    dap_log_compliance(LogLevel.INFO, format_log_message("FACEBOOK", defendant_name, defendant_facebook, dt))
    return dt


def normalize(to_normalize):
    return to_normalize.title()


def process_matches():
    matched_cases = db_get_matched_cases()
    for mc in matched_cases:
        case_number = mc['case_number']
        if mc['DEFENDANT_STREET']:
            send_snailmail(mc['court_name'], mc['case_number'], mc['date_filed'], normalize(mc['plaintiff_name']),
            normalize(mc['defendant_name']), mc['defendant_house'], normalize(mc['defendant_street']), mc['defendant_apt'],
            normalize(mc['defendant_city']), mc['defendant_state'], mc['defendant_zip'])
                                                 
            now = datetime.now()
            mail_time_stamp = now.isoformat()
            email_time_stamp = "NONE"
            fb_time_stamp = "NONE"

            if mc["defendant_email"]:
                email_time_stamp = send_email(mc["court_name"], mc["case_number"], mc["date_filed"], mc["plaintiff_name"], mc["defendant_name"], mc["defendant_email"])

            #if mc["defendant_facebook"]:
            #    fb_time_stamp = send_facebook(mc["court_name"], mc["case_number"], mc["date_filed"], mc["plaintiff_name"], mc["defendant_name"], mc["defendant_facebook"])

            database.db_move_to_processed_cases(case_number, mail_time_stamp, email_time_stamp, fb_time_stamp)
        else:
            db_move_to_incomplete_pipl(case_number)
    return 0

# main program

def main():
    process_matches()
    return 0


main()
