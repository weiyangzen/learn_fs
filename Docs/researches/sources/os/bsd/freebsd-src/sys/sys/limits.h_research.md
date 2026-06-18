# File Research: sources/os/bsd/freebsd-src/sys/sys/limits.h

Defines standard integer and system limits by mapping to machine-provided `_limits.h` values and visibility macros. It covers char, signed/unsigned char, short, int, long, and optionally long long min/max values.

C23 visibility adds `*_WIDTH` macros. POSIX/XSI visibility adds `SSIZE_MAX`, `SIZE_T_MAX`, `OFF_MAX`, `OFF_MIN`, `LONG_BIT`, `WORD_BIT`, and `MQ_PRIO_MAX`. BSD visibility adds uid/gid and quad/uquad limits.
