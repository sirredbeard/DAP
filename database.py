import sqlite3
from datetime import datetime
from dap_logging import dap_log_database, LogLevel

def connect_database():
    return sqlite3.connect('dap.sqlite')


def db_get_latest_case_number(court_name):
    dap_log_database(LogLevel.DEBUG, "getting latest case number")
    conn = connect_database()
    cur = conn.cursor()

    cur.execute('select CASE_NUMBER from CASE_NUMBER where COURT_NAME=?', (court_name,))

    last_successful_case_number = cur.fetchone()[0]
    conn.close()
    return last_successful_case_number


def db_write_latest_case_number(court_name, last_successful_case_number):
    dap_log_database(LogLevel.INFO,
        'recording last successful case number: ' + court_name + '-' +
        str(datetime.now().year) + '-CV-' + str(last_successful_case_number)
    )

    conn = connect_database()
    cur = conn.cursor()

    cur.execute('update CASE_NUMBER set CASE_NUMBER=? where COURT_NAME=?', (last_successful_case_number, court_name,))
    conn.commit()
    conn.close()
    return 0


def db_write_new_case(court_name, last_successful_case_number, year, judge_name, date_filed, time_filed, plaintiff_name, plaintiff_counsel, defendant_name, defendant_counsel, civil_action, action_description):
    conn = connect_database()
    cur = conn.cursor()

    try:
        cur.execute('insert into NEW_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, '
                    'PLAINTIFF_NAME, PLAINTIFF_COUNSEL, DEFENDANT_NAME, DEFENDANT_COUNSEL, CIVIL_ACTION, ACTION_DESCRIPTION) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (court_name, last_successful_case_number, year, judge_name, date_filed, time_filed, plaintiff_name, plaintiff_counsel, defendant_name, defendant_counsel, civil_action, action_description))
    except sqlite3.IntegrityError as err:
        dap_log_database(LogLevel.ERROR, "case number: %i is already in NEW_CASE ignoring" % last_successful_case_number)

    conn.commit()
    conn.close()

    return 0


def db_screen_cases():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        insert into POSSIBLE_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, PLAINTIFF_COUNSEL, DEFENDANT_NAME, DEFENDANT_COUNSEL, CIVIL_ACTION, ACTION_DESCRIPTION)
        select distinct NC.COURT_NAME,
                        NC.CASE_NUMBER,
                        NC.YEAR,
                        NC.JUDGE,
                        NC.DATE_FILED,
                        NC.TIME_FILED,
                        NC.PLAINTIFF_NAME,
                        NC.PLAINTIFF_COUNSEL,
                        NC.DEFENDANT_NAME,
                        NC.DEFENDANT_COUNSEL,
                        NC.CIVIL_ACTION,
                        NC.ACTION_DESCRIPTION
        from NEW_CASE NC,
             CREDITOR
                 left join POSSIBLE_CASE PC on NC.CASE_NUMBER = PC.CASE_NUMBER
        where PC.CASE_NUMBER is null
          and NC.PLAINTIFF_NAME like '%' || CREDITOR || '%'
    """)

    cur.execute("""
        insert into REJECTED_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, PLAINTIFF_COUNSEL, DEFENDANT_NAME, DEFENDANT_COUNSEL, CIVIL_ACTION, ACTION_DESCRIPTION, REJECTED_REASON)
        select distinct NC.COURT_NAME,
                        NC.CASE_NUMBER,
                        NC.YEAR,
                        NC.JUDGE,
                        NC.DATE_FILED,
                        NC.TIME_FILED,
                        NC.PLAINTIFF_NAME,
                        NC.PLAINTIFF_COUNSEL,
                        NC.DEFENDANT_NAME,
                        NC.DEFENDANT_COUNSEL,
                        NC.CIVIL_ACTION,
                        NC.ACTION_DESCRIPTION,
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


def db_move_to_matched_cases(case_number, defendant_house, defendant_street, defendant_apt, defendant_city, defendant_zip, defendant_email,
                             defendant_facebook):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        insert into MATCHED_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, PLAINTIFF_COUNSEL,
                                  DEFENDANT_NAME, DEFENDANT_COUNSEL, CIVIL_ACTION, ACTION_DESCRIPTION, DEFENDANT_HOUSE, DEFENDANT_STREET,
                                  DEFENDANT_APT, DEFENDANT_CITY, DEFENDANT_STATE, DEFENDANT_ZIP, DEFENDANT_EMAIL, DEFENDANT_FACEBOOK)
        select PC.COURT_NAME,
               PC.CASE_NUMBER,
               PC.YEAR,
               PC.JUDGE,
               PC.DATE_FILED,
               PC.TIME_FILED,
               PC.PLAINTIFF_NAME,
               PC.PLAINTIFF_COUNSEL,
               PC.DEFENDANT_NAME,
               PC.DEFENDANT_COUNSEL,
               PC.CIVIL_ACTION,
               PC.ACTION_DESCRIPTION,
               :defendant_house,
               :defendant_street, 
               :defendant_apt,
               :defendant_city, 
               'GA',
               :defendant_zip, 
               :defendant_email,
               :defendant_facebook
        from POSSIBLE_CASE PC
        where PC.CASE_NUMBER=:case_number
    """,
                {'case_number': case_number, 'defendant_house': defendant_house, 'defendant_street': defendant_street, 'defendant_apt': defendant_apt, 
                'defendant_city': defendant_city, 'defendant_zip': defendant_zip, 'defendant_email': defendant_email,'defendant_facebook': defendant_facebook})


    cur.execute("delete from POSSIBLE_CASE where CASE_NUMBER=?", (case_number,))

    conn.commit()
    conn.close()

    return 0

def db_move_to_unmatched_cases(case_number):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        insert or REPLACE into REJECTED_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, PLAINTIFF_COUNSEL, DEFENDANT_NAME, DEFENDANT_COUNSEL, CIVIL_ACTION, ACTION_DESCRIPTION, REJECTED_REASON)
        select distinct PC.COURT_NAME,
                        PC.CASE_NUMBER,
                        PC.YEAR,
                        PC.JUDGE,
                        PC.DATE_FILED,
                        PC.TIME_FILED,
                        PC.PLAINTIFF_NAME,
                        PC.PLAINTIFF_COUNSEL,
                        PC.DEFENDANT_NAME,
                        PC.DEFENDANT_COUNSEL,
                        PC.CIVIL_ACTION,
                        PC.ACTION_DESCRIPTION,
                        'NO PIPL MATCH'
        from POSSIBLE_CASE PC
        where PC.CASE_NUMBER=:case_number
    """,
                {'case_number': case_number})


    cur.execute("delete from POSSIBLE_CASE where CASE_NUMBER=?", (case_number,))

    conn.commit()
    conn.close()

    return 0

def db_move_to_processed_cases(case_number, mail_time_stamp, email_time_stamp, fb_time_stamp):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        insert or REPLACE into PROCESSED_CASE (COURT_NAME, CASE_NUMBER, YEAR, JUDGE, DATE_FILED, TIME_FILED, PLAINTIFF_NAME, PLAINTIFF_COUNSEL, DEFENDANT_NAME, DEFENDANT_COUNSEL, CIVIL_ACTION, ACTION_DESCRIPTION, DEFENDANT_HOUSE, DEFENDANT_STREET, DEFENDANT_APT, DEFENDANT_CITY, DEFENDANT_STATE, DEFENDANT_ZIP, DEFENDANT_EMAIL, DEFENDANT_FACEBOOK, MAIL_TIMESTAMP, EMAIL_TIMESTAMP, FB_TIMESTAMP)
        select distinct MC.COURT_NAME,
                        MC.CASE_NUMBER,
                        MC.YEAR,
                        MC.JUDGE,
                        MC.DATE_FILED,
                        MC.TIME_FILED,
                        MC.PLAINTIFF_NAME,
                        MC.PLAINTIFF_COUNSEL,
                        MC.DEFENDANT_NAME,
                        MC.DEFENDANT_COUNSEL,
                        MC.CIVIL_ACTION,
                        MC.ACTION_DESCRIPTION,
                        DEFENDANT_HOUSE,
                        DEFENDANT_STREET,
                        DEFENDANT_APT,
                        DEFENDANT_CITY,
                        DEFENDANT_STATE,
                        DEFENDANT_ZIP,
                        DEFENDANT_EMAIL,
                        DEFENDANT_FACEBOOK,
                        :mail_time_stamp,
                        :email_time_stamp,
                        :fb_time_stamp
        from MATCHED_CASE MC
        where MC.CASE_NUMBER=:case_number
    """,
                {'case_number': case_number, 'mail_time_stamp': mail_time_stamp, 'email_time_stamp':email_time_stamp, 'fb_time_stamp': fb_time_stamp})


    cur.execute("delete from MATCHED_CASE where CASE_NUMBER=?", (case_number,))

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
