from datetime import datetime
from enum import Enum

SessionLogNumber = 1

PIPL_LOG = "pipl.log"
CLICKSEND_LOG = "clicksend.log"
LOB_LOG = "lob.log"
COMPLIANCE_LOG = "compliance.log"
GENERAL_LOG = "general.log"


class LogType(Enum):
    """
    Types of logging
    """
    PIPL = 0
    CLICKSEND = 1
    LOB = 2
    COMPLIANCE = 3
    GENERAL = 4


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
    LogType.COMPLIANCE:    LogLevel.CRITICAL,
    LogType.GENERAL:       LogLevel.ERROR,
}


LOG_TOFILE_MIN = {
    LogType.PIPL:          LogLevel.INFO,
    LogType.CLICKSEND:     LogLevel.DEBUG,
    LogType.LOB:           LogLevel.DEBUG,
    LogType.COMPLIANCE:    LogLevel.DEBUG,
    LogType.GENERAL:       LogLevel.DEBUG,
}


def check_notify(type, level):
    """
    Check logging level and whether to notify system administrator.

    Default log level to notify at if LogType not defined in dap_config.py
    is LogType.CRITICAL.
    """
    return level.value >= LOG_NOTIFY_MIN.setdefault(type, LogLevel.CRITICAL).value


def check_tofile(type, level):
    """
    Check logging level and whether to write the message to file.

    Default log level to write to file if LogType not defined in dap_config.py
    is LogType.INFO
    """
    return level.value >= LOG_TOFILE_MIN.setdefault(type, LogLevel.INFO).value


def notify_admin(message):
    # TODO: notify administrator somehow. email?
    pass


def log_to_file(file, message):
    f = open(file, 'a')

    # Splits up multi-line messages and places
    # tab break at beginning of line for lines
    # after the first (if they exist)
    lines = message.split('\n')
    f.write(lines[0] + '\n')
    lines.pop(0)

    for i in range(0, len(lines)):
        f.write('\t' + lines[i] + '\n')

    f.close()


def dap_log(type = LogType.GENERAL, level = None, message = ""):
    """
    Handle all specific types of logging, offering ability to notify
    system admin if level matches notify severity level set in dap_config.py

    To save on processing, if you have multi-line log entries it is best
    to format them as-so with newline characers '\n' instead of multiple
    calls to log()

    When passed no type defaults to general log. Level MUST be set
    """

    global SessionLogNumber

    if not level or not isinstance(level, LogLevel):
        raise ValueError("Please supply a valid logging level!")

    # Check whether we should log
    if not check_tofile(type, level):
        return

    # Add log level prefix
    message = str(datetime.now()) + " " + "[ " + str(SessionLogNumber) + " ] " + level.name + " - " + str(type) + " - " + message

    # Check whether we should notify an administrator
    if check_notify(type, level):
        notify_admin(message)

    # Write to the correct log file
    if not type or type == LogType.GENERAL:
        log_to_file(GENERAL_LOG, message)

    elif type == LogType.PIPL:
        log_to_file(PIPL_LOG, message)

    elif type == LogType.CLICKSEND:
        log_to_file(CLICKSEND_LOG, message)

    elif type == LogType.LOB:
        log_to_file(LOB_LOG, message)

    elif type == LogType.COMPLIANCE:
        log_to_file(COMPLIANCE_LOG, message)

    SessionLogNumber += 1