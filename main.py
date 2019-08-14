#!/usr/bin/env python3

from dap_logging import dap_logging_init, dap_logging_close

try:
    dap_logging_init()
    import get_cases
    import screen_cases
    import identify_cases
    import send_letters
finally:
    dap_logging_close()