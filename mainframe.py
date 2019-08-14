import random
import time

from py3270 import Emulator

from mainframe_credentials import MainframeIP, MainframeUsername, MainframePassword
from dap_logging import dap_log_compliance, dap_log_mainframe, LogLevel

em = Emulator()


def mainframe_open_connection():
    dap_log_mainframe(LogLevel.DEBUG, "connecting to mainframe")

    global em
    #em = Emulator(visible=True)
    em = Emulator()
    em.connect(MainframeIP)
    mainframe_random_wait()  # this is necessary because mainframe response time can vary, the delay is worth it

    dap_log_compliance(LogLevel.INFO, "mainframe connection established")

    dap_log_mainframe(LogLevel.DEBUG, "selecting mainframe application")
    em.fill_field(20, 21, 'B', 1)
    em.send_enter()
    mainframe_random_wait()


def mainframe_login():
    dap_log_mainframe(LogLevel.DEBUG, "logging into mainframe")
    dap_log_mainframe(LogLevel.DEBUG, "sending username")
    em.send_string(MainframeUsername)
    em.send_enter()
    mainframe_random_wait()
    dap_log_mainframe(LogLevel.DEBUG, "sending password")
    em.send_string(MainframePassword)
    em.send_enter()
    mainframe_random_wait()


def mainframe_check_login_worked():
    # this is necessary because the mainframe will occasionally report the user being logged in already, this can be forced by attempting the login again
    dap_log_mainframe(LogLevel.DEBUG, "checking if user already logged in")
    if em.string_found(23, 21, 'IS ALREADY IN USE AT TERMINAL'):
        dap_log_mainframe(LogLevel.INFO, "user already logged on, trying again")
        return 1
    elif em.string_found(5, 19, 'Courts Automated Tracking System'):
        dap_log_mainframe(LogLevel.INFO, "login successful")
        return 0

    # ! insert handling for login failure (sometimes need to try a second time)


def mainframe_select_CATS():
    # CATS = courts automated tracking system
    dap_log_mainframe(LogLevel.DEBUG, "selecting CATS function")
    em.send_string('1')
    em.send_enter()
    mainframe_random_wait()


def mainframe_open_docket_search():
    dap_log_mainframe(LogLevel.DEBUG, "opening docket search page")
    em.send_string('Q')
    em.send_string('DCKT')
    em.send_enter()
    mainframe_random_wait()


def mainframe_search_case(court_name, case_number):
    dap_log_mainframe(LogLevel.DEBUG, "searching mainframe for case: %s%i" % (court_name, case_number))
    em.send_string(court_name, ypos=10, xpos=47)
    em.send_enter()
    em.send_string("CV", ypos=14, xpos=47)
    em.send_string(str(case_number), ypos=16, xpos=47)
    em.send_enter()
    mainframe_random_wait()


def mainframe_check_case_exists():
    dap_log_mainframe(LogLevel.DEBUG, "checking to see if case exists")
    check_exists_read = em.string_get(24, 15, 4)
    if check_exists_read == "CASE":
        dap_log_mainframe(LogLevel.DEBUG, "case not found")
        return 0
    else:
        dap_log_mainframe(LogLevel.DEBUG, "case found")
        return 1


def mainframe_parse_case():
    dap_log_mainframe(LogLevel.DEBUG, "parsing first page of case file")
    judge_name = em.string_get(7, 14, 20).strip()
    date_filed = em.string_get(10, 29, 10).strip()
    time_filed = em.string_get(10, 67, 5).strip()
    year = em.string_get(4, 33, 4).strip()
    dap_log_mainframe(LogLevel.DEBUG, "navigating additional pages of case file")
    em.send_enter()
    mainframe_random_wait()
    civil_action = em.string_get(8,38,10).strip()
    action_description = em.string_get(8,49,10).strip()
    em.send_enter()
    mainframe_random_wait()

    dap_log_mainframe(LogLevel.DEBUG, "getting party names")
    for x in range(9, 20):
        check_party = em.string_get(x, 2, 3)

        name = em.string_get(x, 38, 33).strip()
        name = " ".join(name.split())

        if check_party == "D D":
            defendant_name = name

        elif check_party == "P P":
            plaintiff_name = name

        elif check_party == "A P":
            plaintiff_counsel = name

        elif check_party == "C D":
            defendant_counsel = name

    try: plaintiff_counsel
    except:
        dap_log_mainframe(LogLevel.ERROR, "plaintiff counsel empty, setting \'NONE\'")
        plaintiff_counsel = "NONE"
    
    try: defendant_counsel
    except:
        dap_log_mainframe(LogLevel.ERROR, "defendant counsel empty, setting \'NONE\'")
        defendant_counsel = "NONE"

    try: defendant_name
    except UnboundLocalError:
        dap_log_mainframe(LogLevel.CRITICAL, "defendant name field empty")
        return


    try: plaintiff_name 
    except UnboundLocalError:   
        dap_log_mainframe(LogLevel.CRITICAL, "plaintiff name empty")
        return

    dap_log_mainframe(LogLevel.INFO,
        "judge name: %s\ndate filed: %s\ntime filed: %s\ncivil action code: %s\naction description: %s\ndefendant name: %s\nplaintiff name: %s\nplaintiff counsel: %s\ndefendant counsel: %s"
        % (judge_name, date_filed, time_filed, civil_action, action_description, defendant_name, plaintiff_name, plaintiff_counsel, defendant_counsel)
    )
    
    return year, judge_name, date_filed, time_filed, plaintiff_name, plaintiff_counsel, defendant_name, defendant_counsel, civil_action, action_description


def mainframe_reset():  # returns to page where CATS is selected
    em.send_pf7()
    em.send_pf7()
    mainframe_random_wait()


def mainframe_close_connection():  # closes persistent connection to mainframe
    em.terminate()


def mainframe_random_wait():
    random_num = random.uniform(1, 3)
    #print('pausing for ' + str(random_num) + ' seconds')
    time.sleep(random_num)
