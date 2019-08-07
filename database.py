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

    try:
        cur.execute('insert into NEW_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, '
                    'PLAINTIFF_NAME, DEFENDANT_NAME) values (?, ?, ?, ?, ?, ?, ?, ?)',
                    (court_name, last_successful_case_number, year, judge_name, date_filed, time_filed, plaintiff_name,
                     defendant_name))
    except sqlite3.IntegrityError as err:
        print(
            'case number: ' + str(last_successful_case_number) + ' is already in NEW_CASE ignoring')

    conn.commit()
    conn.close()

    return 0


def db_screen_cases():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        insert into POSSIBLE_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, DEFENDANT_NAME)
        select distinct NC.COURT_NAME,
                        NC.CASE_NUMBER,
                        NC.YEAR,
                        NC.JUDGE,
                        NC.DATE_FILED,
                        NC.TIME_FILED,
                        NC.PLAINTIFF_NAME,
                        NC.DEFENDANT_NAME
        from NEW_CASE NC,
             CREDITOR
                 left join POSSIBLE_CASE PC on NC.CASE_NUMBER = PC.CASE_NUMBER
        where PC.CASE_NUMBER is null
          and NC.PLAINTIFF_NAME like '%' || CREDITOR || '%'
    """)

    cur.execute("""
        insert into REJECTED_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, DEFENDANT_NAME, REJECTED_REASON)
        select distinct NC.COURT_NAME,
                        NC.CASE_NUMBER,
                        NC.YEAR,
                        NC.JUDGE,
                        NC.DATE_FILED,
                        NC.TIME_FILED,
                        NC.PLAINTIFF_NAME,
                        NC.DEFENDANT_NAME,
                        'UNKNOWN CREDITOR'
        from NEW_CASE NC,
             CREDITOR
                 left join REJECTED_CASE RC on NC.CASE_NUMBER = RC.CASE_NUMBER
                 left join POSSIBLE_CASE PC on NC.CASE_NUMBER = PC.CASE_NUMBER
        where RC.CASE_NUMBER is null and PC.CASE_NUMBER is null
          and NC.PLAINTIFF_NAME not like '%' || CREDITOR || '%'    
    """)

    cur.execute("delete from NEW_CASE")

    conn.commit()
    conn.close()

    return 0


def db_get_possible_cases():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute('select CASE_NUMBER, DEFENDANT_NAME from POSSIBLE_CASE')

    possible_cases = cur.fetchall()

    conn.close()
    return possible_cases


def db_move_to_matched_cases(case_number, defendant_street, defendant_city, defendant_zip, defendant_email,
                             defendant_facebook):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        insert into MATCHED_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, 
                                  DEFENDANT_NAME, DEFENDANT_STATE, DEFENDANT_STREET, DEFENDANT_CITY, DEFENDANT_ZIP, DEFENDANT_EMAIL,
                                  DEFENDANT_FACEBOOK)
        select PC.COURT_NAME,
               PC.CASE_NUMBER,
               PC.YEAR,
               PC.JUDGE,
               PC.DATE_FILED,
               PC.TIME_FILED,
               PC.PLAINTIFF_NAME,
               PC.DEFENDANT_NAME,
               'GA',
               :defendant_street, 
               :defendant_city, 
               :defendant_zip, 
               :defendant_email,
               :defendant_facebook
        from POSSIBLE_CASE PC
        where PC.CASE_NUMBER=:case_number
    """,
                {'case_number': case_number, 'defendant_street': defendant_street, 'defendant_city': defendant_city,
                 'defendant_zip': defendant_zip, 'defendant_email': defendant_email,
                 'defendant_facebook': defendant_facebook})

    cur.execute("delete from POSSIBLE_CASE where CASE_NUMBER=?", (case_number,))

    conn.commit()
    conn.close()

    return 0


def db_get_matched_cases():
    conn = connect_database()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute('select * from MATCHED_CASE')

    matched_cases = cur. fetchall()

    conn.close()
    return matched_cases
