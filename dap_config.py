from logging import LogType, LogLevel

# TODO: replace these config dicts with config JSON files that are
#   read and parsed on DAP start?

LOG_NOTIFY_MIN = {
    """
    Allows you to specify the minimum logging level defined in logging.py
    for each LogType at which it should notify the system administrator
    """
    LogType.PIPL :          LogType.CRITICAL,
    LogType.CLICKSEND :     LogType.CRITICAL,
    LogType.LOB :           LogType.CRITICAL,
    LogType.COMPLIANCE :    LogType.CRITICAL,
    LogType.GENERAL :       LogType.ERROR,
}

LOG_TOFILE_MIN = {
    """
    Allows you to specific the minimum logging level defined in logging.py
    for each LogType at which the message should be logged to file
    """
    LogType.PIPL :          LogType.WARN,
    LogType.CLICKSEND :     LogType.WARN,
    LogType.LOB :           LogType.WARN,
    LogType.COMPLIANCE :    LogType.WARN,
    LogType.GENERAL :       LogType.WARN,
}