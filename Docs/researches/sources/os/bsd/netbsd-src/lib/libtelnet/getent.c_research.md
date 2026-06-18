# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/getent.c

## Purpose
Wraps terminal capability lookup for telnet code.

## Main Interfaces
Defines `getent(char *, char *)` and, outside Solaris builds, `getstr(char *, char **)`.

## Control Flow And State
With `HAS_CGETENT`, `getent` queries `/etc/gettytab` using `cgetent` and stores the returned entry in a static `area`. `getstr` retrieves string capabilities from that entry using `cgetstr`. Without `HAS_CGETENT`, both functions return failure/null.

## Dependencies
Uses libc capability database APIs when enabled and application prototypes from `misc-proto.h`.

## Risks And Notes
The static `area` is shared process state. The first `getent` argument is unused in the cgetent implementation.
