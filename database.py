from datetime import datetime
import sqlite3


def db_get_latest_case_number(court_name):
    print("getting latest case number")
    conn = sqlite3.connect('dap.sqlite')
    cur = conn.cursor()

    cur.execute('select CASES from CASENUMBERS where COURT=?', (court_name,))

    last_successful_case_number = cur.fetchone()
    conn.close()
    return last_successful_case_number


def db_write_latest_case_number(court_name, last_successful_case_number):
    print(
        'recording last successful case number: ' + court_name + '-' +
        str(datetime.now().year) + '-CV-' + str(last_successful_case_number))

    conn = sqlite3.connect('dap.sqlite')
    cur = conn.cursor()

    cur.execute('update CASENUMBERS set CASES=? where COURT=?', (last_successful_case_number, court_name,))
    conn.commit()
    conn.close()
    return 0


def db_write_new_case(court_name, last_successful_case_number, judge_name, date_filed, time_filed, plaintiff_name,
                      defendant_name):
    conn = sqlite3.connect('dap.sqlite')
    cur = conn.cursor()

    cur.execute('insert into NEWCASES (COURT_NAME, CASENO, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, '
                'DEFENDANT_NAME) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (court_name, last_successful_case_number, date_filed.year, judge_name, date_filed.isoformat(),
                 time_filed.isoformat(), plaintiff_name, defendant_name,))
    conn.commit()
    conn.close()

    # ! format plaintiff_name removing long spaces
    return 0


# main program

def main():
    print(db_get_latest_case_number('SU'))
    db_write_latest_case_number('SU', 30)

    db_write_new_case('CR', 345, 'Yo', datetime.now().date(), datetime.now().time(), 'example',
                      'Carlos Ramirez')
    return 0


main()
