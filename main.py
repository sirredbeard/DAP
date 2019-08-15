#!/usr/bin/env python3

from dap_logging import dap_logging_init, dap_logging_close, dap_log_general

try:
    dap_logging_init(debug = True)
    import get_cases
    import screen_cases
    import identify_cases
    import send_letters
except Exception as e:
    dap_log_general(LogLevel.CRITICAL, "exception encountered [%i]: %s" % (e.errno, e.strerror))
finally:
    dap_logging_close()