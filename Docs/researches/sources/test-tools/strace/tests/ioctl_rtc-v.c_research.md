<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-v.c -->
# sources/test-tools/strace/tests/ioctl_rtc-v.c

Purpose: verbose RTC ioctl variant. It defines `VERBOSE 1` before including `ioctl_rtc.c`.

Important APIs/types/functions: Inherits all RTC helpers from the base file; verbose mode mainly affects `print_rtc_time`, adding weekday, yearday, and daylight-saving fields.

Control flow: same command matrix as `ioctl_rtc.c`, with verbose time struct output for alarm, read/set time, and wake alarm commands.

State and persistence behavior: local RTC structs only; invalid fd prevents hardware changes.

Dependencies/integration points: validates strace verbose expected output for RTC time structures.

Risks and test signals: field values come from deterministic fill patterns. Passing output confirms verbose RTC time field rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc-v.c -->
