from logging import LogType, LogLevel

LOG_NOTIFY_MIN = {
    """
    Allows you to specify the minim logging level defined in logging.py
    for each LogType for which it should notify the system administrator
    """
    LogType.PIPL :          LogType.CRITICAL,
    LogType.ClickSend :     LogType.CRITICAL,
    LogType.LOB :           LogType.CRITICAL,
    LogType.COMPLIANCE :    LogType.CRITICAL,
    LogType.General :       LogType.Error,
}