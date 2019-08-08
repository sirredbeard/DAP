#!/usr/bin/env python3

# library dependencies

from datetime import datetime

# app dependencies

import database
from api_interfaces import *
from api_keys import *

# functions
from database import db_get_matched_cases


def send_snail_mail(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_street,
                    defendant_city, defendant_state, defendant_zip):
    mr = api_lob(court_name, case_number_, date_filed, plaintiff_name, defendant_name, defendant_street,
                           defendant_city, defendant_state, defendant_zip)
    if mr["success"]:

        # if successful
        #   - record time and date for return as snail_mail_timestamp
        #   - log this was run on this date/time to compliance.log
        snail_mail_timestamp = datetime.now()
        dap_log(LogType.COMPLIANCE, LogLevel.INFO,
                f"court_name={court_name}, case_number={case_number_}, " +
                f"id={mr['id']}, expected_delivery_date={mr['expected_delivery_date']}, " +
                f"tracking_number={mr['tracking_number']}")
        return snail_mail_timestamp


def send_email(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email):
    email_results = api_clicksend(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_email)
    # if successful
    #   - record time and date for return as email_timestamp
    #   - log this was run on this date/time to compliance.log
    # return email_timestamp


def send_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name, defendant_facebook):
    facebook_results = api_facebook(court_name, case_number, date_filed, plaintiff_name, defendant_name,
                                    defendant_facebook)
    # if successful
    #   - record time and date for return as facebook_timestamp
    #   - log this was run on this date/time to compliance.log
    # return facebook_timestamp


def normalize(to_normalize):
    # ! convert variable passed from ALL CAPS to Normal Capitalization
    return to_normalize.title()


def process_matches():
    # ! to implement:

    matched_cases = db_get_matched_cases()
    for mc in matched_cases:
        if mc['DEFENDANT_STREET']:
            snailmail_timestamp = send_snail_mail(mc['court_name'], mc['case_number'],
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
