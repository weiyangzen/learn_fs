# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yperr_string.c

## Purpose
Implements `yperr_string()`, converting YP client error codes to human-readable strings.

## Behavior
Returns constant strings for all known `YPERR_*` values and formats unknown values into a static 80-byte buffer.

## Dependencies
Depends on `rpcsvc/ypclnt.h`, `snprintf()`, libc namespace support, and weak aliasing.

## Risks And Notes
The unknown-error path is not thread-safe because it uses a shared static buffer.
