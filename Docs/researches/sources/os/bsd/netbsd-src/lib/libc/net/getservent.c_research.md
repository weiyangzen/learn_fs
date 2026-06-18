# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservent.c

Non-reentrant service database API wrappers. It defines the global `_servent_data` and, under `_REENTRANT`, `_servent_mutex`.

`setservent()`, `endservent()`, and `getservent()` serialize access to the global service state and call their `_r` equivalents. Returned records live in the shared global state, so callers needing independent storage use the reentrant functions.
