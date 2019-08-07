from enum import Enum
from dap_config import LOG_NOTIFY_MIN, LOG_TOFILE_MIN

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
    INFO = 0
    WARN = 1
    ERROR = 2
    CRITICAL = 3

LogPrefix = {
    """
    Prefix to append to messages in logs / messages
    """
    LogLevel.INFO :     "INFO: ",
    LogLevel.WARN :     "WARN: ",
    LogLevel.ERROR :    "ERROR: ",
    LogLevel.CRITICAL : "CRITICAL: ",
}

def check_notify(type, level):
    """
    Check logging level and whether to notify system administrator.

    Default log level to notify at if LogType not defined in dap_config.py
    is LogType.CRITICAL.
    """
    return level >= LOG_NOTIFY_MIN.setdefault(type, LogLevel.CRITICAL)

def check_tofile(type, level):
    """
    Check logging level and whether to write the message to file.

    Default log level to write to file if LogType not defined in dap_config.py
    is LogType.WARN
    """
    return level >= LOG_TOFILE_MIN.setdefault(type, LogLevel.WARN)

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

def log(type = LogType.GENERAL, level = None, message = ""):
    """
    Handle all specific types of logging, offering ability to notify
    system admin if level matches notify severity level set in dap_config.py

    To save on processing, if you have multi-line log entries it is best
    to format them as-so with newline characers '\n' instead of multiple
    calls to log()

    When passed no type defaults to general log. Level MUST be set
    """
    if not level or type(level) != LogLevel:
        raise ValueError("Please supply a valid logging level!")

    # TODO: add a log-tofile level minimum? (e.g. enable INFO logging to file)

    # Add log level prefix
    message = LogPrefix[level] + message

    # Check whether we should notify an administrator
    if check_notify(type, level):
        notify_admin(message)

    # Check whether we should log to file
    if not check_tofile(type, level):
        return

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