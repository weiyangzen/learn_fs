# File Research: sources/os/bsd/netbsd-src/lib/libc/net/servent.h

Internal header for service database state and helpers. `struct servent_data` stores plain-file and CDB handles, current service record, alias vector, flags, CDB iterator index, CDB copy buffer, and current parsed line.

It defines service-state flags `_SV_STAYOPEN`, `_SV_CDB`, `_SV_PLAINFILE`, and `_SV_FIRST`, declares the global `_servent_data` and optional mutex, and exposes reentrant public helpers plus internal open/close/parse routines.
