# File Research: sources/os/bsd/openbsd-src/sys/sys/unistd.h

Defines POSIX constants used by `unistd.h` and kernel/user ABI consumers: `_POSIX_VERSION`, `_POSIX_VDISABLE`, unsupported async/prio/sync I/O indicators, access mode bits, seek constants, and pathconf variable ids.

BSD visibility adds legacy `L_SET`/`L_INCR`/`L_XTND`, `struct __tfork`, `struct __kbind`, and kbind size limits. The pathconf ids are explicitly ABI-stable.
