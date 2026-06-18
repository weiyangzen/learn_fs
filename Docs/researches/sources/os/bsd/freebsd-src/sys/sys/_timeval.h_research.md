# File Research: sources/os/bsd/freebsd-src/sys/sys/_timeval.h

Microsecond-resolution time structure.

Key elements:
- Defines `suseconds_t` and `time_t` if needed.
- Defines `struct timeval` with seconds and microseconds.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Used by `gettimeofday(2)` and legacy time interfaces.
- Appears in ABI compatibility helpers and filesystem timestamp/user ABI paths.
