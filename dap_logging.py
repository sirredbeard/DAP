from datetime import datetime
from enum import Enum

session_log_no = 1

PIPL_LOG = "pipl.log"
CLICKSEND_LOG = "clicksend.log"
LOB_LOG = "lob.log"
FACEBOOK_LOG = "facebook.log"
COMPLIANCE_LOG = "compliance.log"
GENERAL_LOG = "general.log"


class LogType(Enum):
    """
    Types of logging
    """
    PIPL = 0
    CLICKSEND = 1
    LOB = 2
    FACEBOOK = 3
    COMPLIANCE = 4
    GENERAL = 5


class LogLevel(Enum):
    """
    Logging levels (severity)
    """
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    CRITICAL = 4


LOG_NOTIFY_MIN = {
    LogType.PIPL:          LogLevel.CRITICAL,
    LogType.CLICKSEND:     LogLevel.CRITICAL,
    LogType.LOB:           LogLevel.CRITICAL,
    LogType.FACEBOOK:      LogLevel.CRITICAL,
    LogType.COMPLIANCE:    LogLevel.CRITICAL,
    LogType.GENERAL:       LogLevel.ERROR,
}


LOG_TOFILE_MIN = {
    LogType.PIPL:          LogLevel.INFO,
    LogType.CLICKSEND:     LogLevel.DEBUG,
    LogType.LOB:           LogLevel.DEBUG,
    LogType.FACEBOOK:      LogLevel.DEBUG,
    LogType.COMPLIANCE:    LogLevel.DEBUG,
    LogType.GENERAL:       LogLevel.DEBUG,
}


def check_notify(log_type, log_level):
    """
    Check logging level and whether to notify system administrator.

    Default log level to notify at if LogType not defined in dap_config.py
    is LogType.CRITICAL.
    """
    return log_level.value >= LOG_NOTIFY_MIN.setdefault(log_type, LogLevel.CRITICAL).value


def check_tofile(log_type, log_level):
    """
    Check logging level and whether to write the message to file.

    Default log level to write to file if LogType not defined in dap_config.py
    is LogType.INFO
    """
    return log_level.value >= LOG_TOFILE_MIN.setdefault(log_type, LogLevel.INFO).value


def notify_admin(message):
    # TODO: notify administrator somehow. email? clicksend
    pass


def log_to_file(filename, message):
    f = open(filename, 'a')

    # Splits up multi-line messages and places
    # tab break at beginning of line for lines
    # after the first (if they exist)
    lines = message.split('\n')
    f.write(lines[0] + '\n')
    lines.pop(0)

    for i in range(0, len(lines)):
        f.write('\t' + lines[i] + '\n')

    f.close()


def dap_log(log_type = LogType.GENERAL, log_level = None, message = ""):
    """
    Handle all specific types of logging, offering ability to notify
    system admin if level matches notify severity level set in dap_config.py

    To save on processing, if you have multi-line log entries it is best
    to format them as-so with newline characers '\n' instead of multiple
    calls to log()

    When passed no type defaults to general log. Level MUST be set
    """

    global session_log_no

    if not log_level or not isinstance(log_level, LogLevel):
        raise ValueError("Please supply a valid logging level!")

    # Check whether we should log
    if not check_tofile(log_type, log_level):
        return

    # Generate log message
    # TODO: format the date for easier log grepping ?
    message = "%s [%s] %s: %s" % (datetime.now(), session_log_no, log_type.name, message)

    # Check whether we should notify an administrator
    if check_notify(log_type, log_level):
        notify_admin(message)

    # Write to the correct log file
    if not log_type or log_type == LogType.GENERAL:
        log_to_file(GENERAL_LOG, message)

    elif log_type == LogType.PIPL:
        log_to_file(PIPL_LOG, message)

    elif log_type == LogType.CLICKSEND:
        log_to_file(CLICKSEND_LOG, message)

    elif log_type == LogType.LOB:
        log_to_file(LOB_LOG, message)

    elif log_type == LogType.FACBEOOK:
        log_to_file(FACEBOOK_LOG, message)

    elif log_type == LogType.COMPLIANCE:
        log_to_file(COMPLIANCE_LOG, message)

    session_log_no += 1