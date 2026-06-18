# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yplib.c

## Purpose
Implements shared YP client binding, unbinding, default-domain, and domain validation logic.

## Main Entry Points
- `_yp_dobind()` obtains or refreshes a domain binding and RPC client.
- `yp_bind()` binds a domain.
- `yp_unbind()` removes a cached binding.
- `__yp_unbind()` destroys a binding’s active client without removing the binding object.
- `yp_get_default_domain()` caches and returns the process domain name.
- `yp_setbindtries()` updates the retry limit.
- `_yp_check()` validates default-domain availability and binding.
- `_yp_invalid_domain()` rejects null, empty, too-long, or slash-containing domains.

## Control Flow
`_yp_dobind()` first checks `/var/run/ypbind.lock` to determine whether ypbind is running. It resets cached bindings across fork by tracking PID. It tries to read `/var/yp/binding/<domain>.2` while locked by ypbind; if unavailable, it contacts local `ypbind` over TCP. Once a YP server address is known, it creates a UDP client for `YPPROG/YPVERS`, sets close-on-exec on the socket, and caches the binding.

## Dependencies
Depends on file locks, binding files, local ypbind RPC service, RPC TCP/UDP client APIs, socket structures, `getdomainname()`, and reentrant mutex wrappers.

## Risks And Notes
Binding state is global per process. Fork detection clears inherited clients. Some error paths print to stderr via RPC helper functions. The reentrant lock is used by `_yp_check()` but not every public operation in other files.
