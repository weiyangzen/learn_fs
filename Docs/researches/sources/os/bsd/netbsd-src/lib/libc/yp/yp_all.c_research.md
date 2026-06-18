# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_all.c

## Purpose
Implements `yp_all()`, streaming all key/value pairs from a YP map through a user callback.

## Behavior
Validates domain, map name, and callback. Binds to the domain, creates a TCP RPC client to the bound YP server, sends a `YPPROC_ALL` request with `ypreq_nokey`, decodes the stream with `xdr_ypall()`, destroys the client, unbinds the domain binding, and maps RPC failure to `YPERR_RPC`.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypreq_nokey`, `xdr_ypall`, RPC client APIs, and shared `_yplib_timeout`.

## Risks And Notes
Unlike the other per-key procedures, this creates a separate TCP client rather than using the cached UDP client. It emits `warnx()` on TCP client creation failure.
