# dap_logging.py usage:
#
# - use dap_logging_init() to initialize the dap_logging system
#
# - call the appropriate helper function found at the bottom of
#   this file (e.g. dap_log_mainframe(), dap_log_database() etc)
#   with a severity level and message
#
# - logging system uses supplied (default if none) config to check
#   each log severity, and if high enough log to file or even
#   notify an administrator via email
#
# - use dap_logging_close() when stopping the dap_logging system
#   to ensure that open log file handles are closed
#
# adding new log types to dap_logging.py:
#
# - add new global variable for your log file string (making sure to prefix
#   with the LOG_FOLDER variable!)
#
# - add a new entry in the LogTypes enum for your new log type
#
# - add a new helper function at the bottom of the file -- creating a
#   LogObject with your LogType enum, log file string and newline tab
#   spacing prefix, then passing this with the log level and message
#   to the global logging session's .log_to() method
#
# - add an option for your new log type in the DEFAULT_CONFIG
#   dictionary found below and delete your old config file to generate a
#   one with the new LogType configuration set
# OR
# - modify your existing JSON config file to add the new log type using
#   other log types in the file to see how to format and what config keys
#   are required to be set
#


import json, os
from datetime import datetime
from enum import Enum


# Log file strings
LOG_FOLDER = "logging/"
MAINFRAME_LOG = LOG_FOLDER + "mainframe.log"
DATABASE_LOG = LOG_FOLDER + "database.log"
PIPL_LOG = LOG_FOLDER + "pipl.log"
CLICKSEND_LOG = LOG_FOLDER + "clicksend.log"
LOB_LOG = LOG_FOLDER + "lob.log"
FACEBOOK_LOG = LOG_FOLDER + "facebook.log"
COMPLIANCE_LOG = LOG_FOLDER + "compliance.log"
GENERAL_LOG = LOG_FOLDER + "general.log"


# Config strings
CONFIG_FILE = LOG_FOLDER + "config.json"
KEY_EMAIL = "admin_email"
KEY_TYPES = "log_types"
KEY_NOTIFY = "level_notify"
KEY_TOFILE = "level_tofile"


class LogType(Enum):
    """
    Types of logging
    """
    MAINFRAME = 0
    DATABASE = 1
    PIPL = 2
    CLICKSEND = 3
    LOB = 4
    FACEBOOK = 5
    COMPLIANCE = 6
    GENERAL = 7


class LogLevel(Enum):
    """
    Logging levels (severity)
    """
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    CRITICAL = 4


class LogObject:
    """
    LogObject: set the type, file string, number of
    tab spaces to use in event of newline in log message    
    """
    def __init__(self, log_type, log_file, newline_tabs = 1):
        self.log_type = log_type
        self.log_file = log_file
        self.newline_tabs = newline_tabs


class LoggingSession:
    """
    LoggingSession: creates logging session which holds
    onto a parsed config and admin email, keeps a counter
    of logs for the session and opens + holds onto file
    handles for supplied log files.

    You may log to these files by supplying an appropriate
    LogObject, severity level and message to the log_to()
    method
    """

    def __init__(self, debug = False):
        """
        Initialize with debug set to false,
        and log count set to 0 for the start
        of this session
        """
        self.debug = debug
        self.config = None
        self.admin_email = None
        self.log_count = 0
        self.file_handles = {}

    def set_config(self, config = {}):
        """
        Set parsed configuration
        """
        self.config = config

    def set_admin_email(self, email):
        """
        Set admin email to use for notifications
        """
        self.admin_email = email

    def get_logtype_config(self, log_type):
        """
        Returns dict with log level priority
        configurations for a specified log type
        """
        if not self.config[log_type]:
            raise ValueError("Log type \'%s\' not found in config" % log_type.name)
        return self.config[log_type]

    def check_tofile(self, log_type, log_level):
        """
        Check whether supplied log level is high
        priority enough to log to file
        """
        return log_level.value >= self.get_logtype_config(log_type)[KEY_TOFILE].value

    def check_notify(self, log_type, log_level):
        """
        Check whether supplied log level is high
        priority enough to notify admin via email
        """
        return log_level.value >= self.get_logtype_config(log_type)[KEY_NOTIFY].value

    def notify_admin(self, message):
        """
        Notify admin email with supplied formatted
        log message
        """
        if self.admin_email:
            # TODO: implement
            pass

    def write_tofile(self, file, message, tab_count = 1):
        """
        Write supplied log message to supplied file handle,
        using the specified number of tab spacings as a prefix
        when newlines are found
        """

        # Write first line to file as-is
        lines = message.split('\n')
        file.write(lines[0] + '\n')

        # In case of newlines, write to file with specified
        # tab space count
        lines.pop(0)
        for i in range(0, len(lines)):
            file.write(tab_count * '\t' + lines[i] + '\n')

        # Flush internal buffer
        file.flush()

    def log_to(self, lobject, log_level, message):
        """
        Check supplied log level against session config to see if
        high priority enough to log to file and even notify an admin
        via email.

        Log type and file is supplied in the LogObject,
        and a file handle is opened and held for any newly passed
        LogObjects.
        """

        # If not already open, open file handle, else grab from dict
        if not lobject.log_type.name in self.file_handles:
            handle = open(lobject.log_file, 'a')
            self.file_handles[lobject.log_type.name] = handle
        else:
            handle = self.file_handles[lobject.log_type.name]

        # Check if level does not reach 'tofile' minimum defined level
        if not self.check_tofile(lobject.log_type, log_level):
            return

        # Print to stdout if debug
        if self.debug:
            print(lobject.log_type.name + ": " + message)

        # Format message, send to admin if high priority enough then
        # write to file
        message = "%s [%s] %s:\t%s %s" % (datetime.now().strftime("%m/%d/%y %H:%M:%S"), self.log_count, lobject.log_type.name, log_level.name, message)
        if self.check_notify(lobject.log_type, log_level):
            self.notify_admin(message)
        self.write_tofile(handle, message, lobject.newline_tabs)

        # Increment session log count
        self.log_count += 1

    def close(self):
        """
        Close any open file handles the LogSession is holding onto
        """
        for key in self.file_handles.keys():
            if self.file_handles[key]: self.file_handles[key].close()


# Global LoggingSession instance
_SESSION = None


# Default logging configuration to use + dump to file
# if none found.
# 
# If adding a new type to the default config, notice
# that enums are converted to their name strings using
# Enum.TYPE.name for storage in JSON.
DEFAULT_CONFIG = {
    KEY_EMAIL:  None,
    KEY_TYPES: {
        LogType.MAINFRAME.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
        LogType.DATABASE.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
        LogType.PIPL.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
        LogType.CLICKSEND.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
        LogType.LOB.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
        LogType.FACEBOOK.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
        LogType.COMPLIANCE.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
        LogType.GENERAL.name: {
                KEY_TOFILE: LogLevel.DEBUG.name,
                KEY_NOTIFY: LogLevel.CRITICAL.name
            },
    }
}


def parse_config(raw):
    """
    Parse the string found in the raw config
    dictionary (straight from JSON) and convert
    these to the appropriate LogType / LogLevel
    enums.

    Returns tuple of config, admin_email
    """
    config = {}

    raw_config = raw[KEY_TYPES]
    for key in raw_config:
        type_config = raw_config[key]
        tofile = type_config[KEY_TOFILE]
        notify = type_config[KEY_NOTIFY]

        log_type = LogType[key]
        tofile_level = LogLevel[tofile]
        notify_level = LogLevel[notify]

        config[log_type] = {
            KEY_TOFILE: tofile_level,
            KEY_NOTIFY: notify_level            
        }

    return config, raw[KEY_EMAIL]


def dap_logging_init(debug = False):
    """
    Initializes the dap_logging system
    """
    global _SESSION

    # Initialize global LoggingSession
    _SESSION = LoggingSession(debug = debug)

    # Check log folder exists, create if not
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    # Check config file exists, create (with defaults) if not
    if not os.path.exists(CONFIG_FILE):
        handle = open(CONFIG_FILE, 'w')
        json.dump(DEFAULT_CONFIG, handle, indent=4)
        handle.close()

    # Read + Parse config file
    handle = open(CONFIG_FILE, 'r')
    raw = json.load(handle)
    config, email = parse_config(raw)
    handle.close()

    # Set found configuration settings
    _SESSION.set_config(config)
    if email: _SESSION.set_admin_email(email)


def dap_logging_close():
    """
    Informs the global LoggingSession to close all
    open file handles
    """
    _SESSION.close()


# Below are helper functions for sending
# logs for predefined log types to the
# global logging session
def dap_log_mainframe(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.MAINFRAME, MAINFRAME_LOG, 5),
        log_level,
        message
    )

def dap_log_database(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.DATABASE, DATABASE_LOG, 5),
        log_level,
        message
    )

def dap_log_pipl(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.PIPL, PIPL_LOG, 5),
        log_level,
        message
    )

def dap_log_clicksend(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.CLICKSEND, CLICKSEND_LOG, 5),
        log_level,
        message
    )

def dap_log_lob(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.LOB, LOB_LOG, 5),
        log_level,
        message
    )

def dap_log_facebook(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.FACEBOOK, FACEBOOK_LOG, 5),
        log_level,
        message
    )

def dap_log_compliance(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.COMPLIANCE, COMPLIANCE_LOG, 5),
        log_level,
        message
    )

def dap_log_general(log_level, message):
    _SESSION.log_to(
        LogObject(LogType.GENERAL, GENERAL_LOG, 5),
        log_level,
        message
    )