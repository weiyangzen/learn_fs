# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.h

## Purpose
`log.h` declares logging APIs and provides no-op/fallback macros for `SMALL` builds.

## Exports
In normal builds it declares logging, debug, syslog, and fatal functions with printf-format attributes. In `SMALL` builds, log calls compile to no-ops and fatal calls exit directly.

## Integration Notes
This header is included across the daemon and parser. It also includes `<stdlib.h>` so `SMALL` fatal macros can call `exit(1)`.
