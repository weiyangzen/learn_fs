# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/time.h

Declares old time and time-zone compatibility APIs.

It includes `<compat/sys/time.h>`, defines `CLK_TCK`, declares old 32-bit-time functions such as `ctime`, `gmtime`, `localtime`, `time`, `mktime`, and many `_r`/timezone variants, plus modern `__*50` clock, nanosleep, and timer functions using `struct timespec`.

This is a broad time32/time64 ABI compatibility header used across old libc consumers.
