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
from dap_logging import dap_log, LogType, LogLevel, format_log_message

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

    # if an e-mail address exists

        # normalize(plaintiff_name, defendant_name)
        # email_time_stamp = send_email(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email)

        email_time_stamp = "NONE"

    # if a facebook address exists

        # normalize(plaintiff_name, defendant_name)
        # fb_time_stamp = send_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook)

        fb_time_stamp = "NONE"

        try: mail_time_stamp
        except: mail_time_stamp = "NONE"
        
        try: email_time_stamp
        except: email_time_stamp = "NONE"

        try: fb_time_stamp
        except: fb_time_stamp = "NONE"
    
        database.db_move_to_processed_cases(case_number, mail_time_stamp, email_time_stamp, fb_time_stamp)

    return 0


# main program

def main():
    process_matches()
    return 0


main()
