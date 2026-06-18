# File Research: sources/os/bsd/netbsd-src/lib/libc/time/asctime.c

## Purpose
Implements `asctime`, `asctime_r`, `ctime`, `ctime_r`, and `ctime_rz` using fixed C/POSIX formatting rather than locale-sensitive `strftime`.

## Key Elements
Formats weekday/month names from static English tables, handles null `tm` by returning placeholder text and `EINVAL`, guards buffer overflow with `snprintf`, pads traditional four-digit years where possible, and supports static or public `asctime_r` depending on POSIX feature macros.

## Dependencies
Uses `private.h`, `namespace.h`, `stdio`, `localtime`, `localtime_r`, `localtime_rz`, and timezone types.

## Behavior/Risks
Static `asctime` storage is shared and non-thread-safe by design. Out-of-range years may use expanded spacing or overflow failure with `EOVERFLOW`; null `timeptr` returns a placeholder string if a buffer exists.
