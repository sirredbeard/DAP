from datetime import datetime
import sqlite3


def connect_database():
    return sqlite3.connect('dap.sqlite')


def db_get_latest_case_number(court_name):
    print("getting latest case number")
    conn = connect_database()
    cur = conn.cursor()

    cur.execute('select CASE_NUMBER from CASE_NUMBER where COURT_NAME=?', (court_name,))

    last_successful_case_number = cur.fetchone()[0]
    conn.close()
    return last_successful_case_number


def db_write_latest_case_number(court_name, last_successful_case_number):
    print(
        'recording last successful case number: ' + court_name + '-' +
        str(datetime.now().year) + '-CV-' + str(last_successful_case_number))

    conn = connect_database()
    cur = conn.cursor()

    cur.execute('update CASE_NUMBER set CASE_NUMBER=? where COURT_NAME=?', (last_successful_case_number, court_name,))
    conn.commit()
    conn.close()
    return 0


def db_write_new_case(court_name, last_successful_case_number, year, judge_name, date_filed, time_filed, plaintiff_name,
                      defendant_name):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute('insert into NEW_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, '
                'DEFENDANT_NAME) values (?, ?, ?, ?, ?, ?, ?, ?)',
                (court_name, last_successful_case_number, year, judge_name, date_filed, time_filed, plaintiff_name,
                 defendant_name))
    conn.commit()
    conn.close()

    # ! format plaintiff_name removing long spaces
    return 0

