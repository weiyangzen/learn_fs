# sources/test-tools/fio/os/windows/posix/include/syslog.h

Purpose: declares a tiny syslog facade for Windows.

Important APIs/types: declares `syslog()`, `openlog()`, and `closelog()` and defines a small set of `LOG_*` priority/option/facility constants.

Control flow and state: `posix.c` lazily opens `syslog.txt` and writes formatted messages with `WriteFile()`.

Dependencies and integration: supports code that logs through syslog APIs without requiring Windows Event Log integration.

Risks: the header declares `syslog()` as returning `int`, while the implementation returns `void`; this is a type mismatch. Priorities, facilities, options, identity strings, and PID behavior are ignored. The file handle is global and unsynchronized.

Test signals: Windows compile warnings should be checked for prototype mismatch; runtime should confirm messages reach `syslog.txt` and failures do not crash.
