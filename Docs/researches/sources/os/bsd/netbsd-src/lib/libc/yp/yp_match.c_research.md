# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_match.c

## Purpose
Implements `yp_match()`, retrieving a value for a key from a YP map, with a small optional in-process cache.

## Behavior
Validates output pointers, domain, map, key, and key length. Binds to the domain, checks the cache for the default domain, sends `YPPROC_MATCH` on a miss, retries on RPC failure, copies returned value into a newly allocated NUL-terminated buffer, optionally caches successful default-domain results, frees XDR response memory, unbinds, and clears output on failure.

## Cache
With `YPMATCHCACHE`, `_yplib_cache` controls TTL seconds. Cache entries are a linked list of map/key/value copies. Expired entries may be reused by `ypmatch_add()`.

## Dependencies
Depends on `_yp_dobind()`, `_yp_domain`, `__yp_unbind()`, RPC/XDR helpers, `ypprot_err()`, `time()`, and malloc/free.

## Risks And Notes
The cache is global and not independently locked in this file. Cache add failure after a successful network lookup changes the result to `YPERR_RESRC` and frees the just-returned output.
