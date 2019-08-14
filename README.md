# DAP

## Debtor Advice Program

Scans a court IBM mainframe for recent cases filed by creditors and sends debtors a letter, e-mail, and/or facebook message about their legal rights.

- Because the mainframe does not provide an address for the defendant, a search is run using the pipl API
- The letter is sent by the lob API
- The e-mail is sent by the clicksend API, which unlike plain smtp reduces likelihood of being marked spam
- The facebook message is sent by the fbchat library

### Dependencies

`$ sudo apt-get install git python3 python3-pip s3270 x3270 -y`

Note: s3270 is in non-free repository.  x3270 is useful for debugging mainframe interactions but not required, see comments in mainframe.py.

```
$ pip3 install py3270 lob piplapis-python fbchat
$ pip3 install git+https://github.com/ClickSend/clicksend-python.git
```

### Components

main.py

    - calls get_cases.py
    - calls screen_cases.py
    - calls identify_cases.py
    - calls send_letters.py

    ```
    NOTE: These four scripts are meant to be run consecutavely in the order above.
    Each step is designed that a failure of one script will not result in data loss.
    Any unprocessed data will simply be picked up and handled in the next pass.
    This script is meant to run every 2-3 hours.
    ```

get_cases.py

    - checks for new cases in all 4 local courts by connecting to mainframe, using py3720 and an internal api in mainframe.py
    - keeps a database of existing case numbers in CASENUMBERS, because case numbers are issued sequentially by year, searches start with last known good+1 and fail after 15 cases are not found
    - stores data from new cases for analysis in NEW_CASE in dap.sqlite

screen_cases.py

    - opens new cases in NEW_CASE
    - screens plaintiff_name for keywords and known creditors which are listed as CREDITOR
    - if a match is found, case is moved to possible cases in POSSIBLE_CASE
    - if a match is not found, case is moved to rejected cases in REJECTEDCASES and noted why

identify_cases.py

    - opens possible cases in POSSIBLE_CASE
    - matches cases in POSSIBLE_CASE to people using the pipl api, via api_interfaces.py
    - if a match is found, case is moved to possible cases in POSSIBLE_CASE
    - if a match is not found, case is moved to rejected cases in REJECTEDCASES and noted why

send_letters.py

    - processes MATCHEDCASES
    - send prospective debtors a letter, e-mail, and/or facebook message based on available data
    - sends letter via USPS via lob api
    - sends e-mail via clicksend api
    - sends facebook message via facebook api, all via via api_interfaces.py
    - saves processed cases to PROCESSEDCASES with time-stamp for any/all of above

api_interfaces.py

    - contains functions for interacting with various apis

api_keys.py (only .example uploaded to github)

    - contains api keys for apis

database.py

    - contains functions for interacting with local sqlite database

mainframe.py

    - contains functions for interacting with court mainframe

mainframe_credentials.py (only .example uploaded to github)

    - stores contains mainframe credentials

dap_logging.py

    - contains functions for logging application events

    - check file for usage information

combine_logs.py

    - combine all logs in logging directory and order based on session
      log count

dap.sqlite, tables:

    - CASENUMBERS - for tracking last known case numbers
    - NEW_CASE - all cases scanned from mainframe
    - POSSIBLE_CASE - cases whose plaintiff contains a keyword from CREDITOR
    - MATCHED_CASE - cases whose defendant has been matched to a person
    - PROCESSED_CASE - cases that were sent letter, e-mail, or facebook message, with time-stamp
    - REJECTED_CASE - cases rejected for no matching creditor or individual
    - CREDITOR - list of creditors and keywords for creditors

logs:

    - mainframe.log - for logging mainframe responses
    - database.log - for logging database events
    - pipl.log - for logging pipl api responses
    - clicksend.log - for logging clicksend api responses
    - lob.log - for logging lob api responses
    - compliance.log - for logging compliance-related activities
    - facebook.log - for logging facebook responses

database.sql

    - create dap.sqlite from scratch

test_data.sql

    - sample data for dap.sqlite