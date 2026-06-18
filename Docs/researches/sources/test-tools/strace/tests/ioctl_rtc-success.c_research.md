<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-success.c -->
# sources/test-tools/strace/tests/ioctl_rtc-success.c

Purpose: injected-success variant for RTC ioctl decoding. It defines `INJECT_RETVAL 42` and includes `ioctl_rtc.c`.

Important APIs/types/functions: Inherits RTC command arrays, `struct rtc_time`, `rtc_wkalrm`, `rtc_pll_info`, `rtc_param`, and helper functions from the base file.

Control flow: included `main` first locks onto injected `RTC_AIE_OFF`, then runs all RTC command groups with successful read-path decoding and injected return text.

State and persistence behavior: local RTC structs only; injection simulates successful kernel writes to output buffers.

Dependencies/integration points: validates syscall injection with RTC decoder output.

Risks and test signals: requires correct injection skip count. Passing output confirms RTC read-ioctl struct expansion under success conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-success.c -->
