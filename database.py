import datetime
import sqlite3


def db_get_latest_case_number(court_name):
    print("getting latest case number")
    conn = sqlite3.connect('dap.sqlite')
    cur = conn.cursor()

    cur.execute('select ID from CASENUMBERS where COURT=?', (court_name,))

    last_successful_case_number = cur.fetchone()
    conn.close()
    return last_successful_case_number

def db_write_latest_case_number(court_name,last_successful_case_number):
    print('recording last successful case number: ' + court_name + '-' + datetime.now().year + '-CV-' + last_successful_case_number)
    conn = sqlite3.connect('dap.sqlite')
    cur = conn.cursor()
    # ! insert handling for writing value stored for respective court_name, stored in CASENUMBERS
    conn.commit()
    conn.close()
    return 0

def db_write_new_case(court_name,last_successful_case_number,judge_name,date_filed,time_filed,plaintiff_name,defendant_name):
    # ! insert handling for writing new cases to NEWCASES
    # ! format plaintiff_name removing long spaces
    return 0