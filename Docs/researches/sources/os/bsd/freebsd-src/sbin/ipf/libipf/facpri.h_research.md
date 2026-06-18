# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.h

This header declares facility/priority conversion functions from `facpri.c`.

It also defines compatibility macros for `LOG_CRON1` and `LOG_CRON2` depending on the platform value of `LOG_CRON`, and temporarily provides `__P()` if missing.

The header expects syslog facility constants to be available to the including translation unit.
