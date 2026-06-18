# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_order.c

## Purpose
Implements `yp_order()`, returning a YP map’s order number.

## Behavior
Validates domain, map, and output pointer. Binds, calls `YPPROC_ORDER`, retries after RPC failures, handles `RPC_PROCUNAVAIL` as a YP server error for NIS+ compatibility mode, writes the returned order number, frees XDR response memory, unbinds, and returns protocol status through `ypprot_err()`.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypreq_nokey`, `xdr_ypresp_order`, and YP retry globals.

## Risks And Notes
`*outorder` is assigned before converting the protocol status, so callers should trust it only when the return code is zero.
