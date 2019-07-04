def mainframe_open_connection():
    print('connecting to mainframe') # mainframe connection is verbose to aid debugging
    em = Emulator()
    # em = Emulator(visible=True) can be useful for debugging to watch process, requires x3270 and X to be running
    em.connect(MainframeIP)
    mainframe_random_wait() # this is necessary because mainframe response time can vary, the delay is worth it

    # ! log a connection was made to compliance.log

    print('selecting mainframe application')
    em.fill_field(20, 21, 'B', 1)
    em.send_enter()
    mainframe_random_wait()

def mainframe_login():
    print ('logging into mainframe')
    print ('sending username')
    em = Emulator()
    em.send_string(MainframeUsername)
    em.send_enter()
    mainframe_random_wait()
    print ('sending password')
    em.send_string(MainframePassword)
    em.send_enter()
    mainframe_random_wait()

def mainframe_check_login_worked():
    print('checking if user is already logged in')  # this is necessary because the mainframe will occasionally report the user being logged in already, this can be forced by attempting the login again
    em = Emulator()
    if em.string_found(23,21,'IS ALREADY IN USE AT TERMINAL'):
        print ('user already logged on, trying again')
        return 1
    elif em.string_found(5,19,'Courts Automated Tracking System'):
        print ('login successful')
        return 0

    # ! insert handling for login failure (sometimes need to try a second time)

def mainframe_select_CATS():
    print ('selecting CATS function') # CATS = courts automated tracking system
    em = Emulator()
    em.send_string('1')
    em.send_enter()
    mainframe_random_wait()

def mainframe_open_docket_search():
    print('opening docket search page')
    em = Emulator()
    em.send_string('Q')
    em.send_string('DCKT')
    em.send_enter()
    mainframe_random_wait()

def mainframe_search_case(court_name,case_number):
    print('searching mainframe for case:' + court_name + )
    em = Emulator()
    em.send_string(court_name, ypos=10, xpos=47)
    em.send_enter()
    em.send_string("CV", ypos=14, xpos=47)
    em.send_string(str(case_number), ypos=16, xpos=47)
    em.send_enter()
    mainframe_random_wait()

def mainframe_check_case_exists():
    print('checking to see if case exists')
    em = Emulator()
    check_exists_read = em.string_get(24, 15, 4)
    if check_exists_read == "CASE":
        print('case found')
        return 0
    else:
        print('case not found')
        return 1

def mainframe_parse_case():
    print('parsing first page of case file')
    em = Emulator()
    judge_name = em.string_get(7, 14, 20)
    date_filed = em.string_get(10, 29, 8)
    time_filed = em.string_get(10, 67, 5)
    print("judge name", judge_name)
    print("date filed", date_filed)
    print("time filed", time_filed)
    print('navigating additional pages of case file')
    em.send_enter()
    mainframe_random_wait()
    em.send_enter()
    mainframe_random_wait()
    print('getting the parties names')
    for x in range(9, 20):
        check_party = em.string_get(x, 2, 1)
        if check_party == "D":
            defendant_name = em.string_get(x, 38, 33)
    for x in range(9, 20):
        check_party = em.string_get(x, 2, 1)
        if check_party == "P":
            plaintiff_name = em.string_get(x, 38, 33)
    print("defendant name", defendant_name)
    print("plaintiff name", plaintiff_name)
    return judge_name,date_filed,time_filed,plaintiff_name,defendant_name

def mainframe_reset(): # returns to page where CATS is selected
    em = Emulator()
    em.send_pf7()
    em.send_pf7()
    mainframe_random_wait()

def mainframe_close_connection(): # closes persistent connection to mainframe
    em = Emulator()
    em.terminate()

def mainframe_random_wait():
    random_num = random.randint(1,5)
    print('pausing for '+random_num+' seconds')
    time.sleep ()