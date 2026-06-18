# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/ypprot_err.c

## Purpose
Implements `ypprot_err()`, translating YP protocol status codes to YP client error codes.

## Behavior
Maps `YP_TRUE` to success and known protocol failures to corresponding `YPERR_*` values, falling back to `YPERR_YPERR`.

## Dependencies
Depends on `rpcsvc/yp_prot.h`, `rpcsvc/ypclnt.h`, and weak aliasing.

## Risks And Notes
The mapping is intentionally lossy because client APIs expose a smaller error taxonomy than the protocol.
