# File Research: sources/teaching/xv6-public/date.h

Defines `struct rtcdate`.

Fields:
- `second`, `minute`, `hour`, `day`, `month`, and `year`.

Used by `lapic.c` CMOS time-reading support and declared in kernel/user interfaces where RTC dates are referenced.
