# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_master.c

## Purpose
Implements `yp_master()`, returning the master server name for a YP map.

## Behavior
Validates output pointer, domain, and map. Binds, calls `YPPROC_MASTER`, retries on RPC failure using binding invalidation, converts protocol status, duplicates the returned master string on success, frees XDR-owned response memory, unbinds, and clears output on failure.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypreq_nokey`, `xdr_ypresp_master`, `ypprot_err()`, and `strdup()`.

## Risks And Notes
The caller owns `*outname`. Allocation failure is reported as `YPERR_RESRC`.
