#!/usr/bin/env python3

import traceback
from dap_logging import dap_logging_init, dap_logging_close, dap_log_general, LogLevel

try:
    dap_logging_init(debug = True)
    import get_cases
    import screen_cases
    import identify_cases
    import send_letters
except Exception as err:
    dap_log_general(LogLevel.CRITICAL, "exception encountered: %s\n%s" % (err, traceback.format_exc()))
finally:
    dap_logging_close()