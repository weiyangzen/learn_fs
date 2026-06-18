# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_maplist.c

## Purpose
Implements `yp_maplist()`, retrieving the list of maps served for a YP domain.

## Behavior
Validates the domain and output pointer, binds to the domain, calls `YPPROC_MAPLIST`, retries after RPC failures by invalidating the binding version, stores the returned linked list in `*outmaplist`, unbinds, and returns protocol status via `ypprot_err()`.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypdomain_wrap_string`, `xdr_ypresp_maplist`, and retry globals.

## Risks And Notes
The code intentionally does not call `xdr_free()` for the response because ownership of the returned maplist is transferred to the caller.
