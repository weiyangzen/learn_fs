# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_first.c

## Purpose
Implements `yp_first()` and `yp_next()` for iterating key/value records in a YP map.

## Behavior
Both functions validate output pointers, domain, map, and key inputs; initialize outputs to null/zero; bind to the domain; issue `YPPROC_FIRST` or `YPPROC_NEXT`; retry by marking `dom_vers = -1` on RPC errors; convert protocol status through `ypprot_err()`; allocate NUL-terminated copies of returned key/value data; free XDR memory; unbind; and clean partial outputs on failure.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `_yplib_timeout`, `_yplib_nerrs`, `_yplib_bindtries`, `xdr_ypreq_nokey`, `xdr_ypreq_key`, `xdr_ypresp_key_val`, and `ypprot_err()`.

## Risks And Notes
Returned key/value data may be binary but is copied with an extra trailing NUL for compatibility. If allocating the value fails after key allocation, cleanup releases the partial key.
