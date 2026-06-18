# File Research: sources/os/bsd/netbsd-src/lib/libc/net/inet6_scopeid.c

KAME-compatibility helpers for embedded IPv6 scope IDs. When compiled with `__KAME__`, `inet6_getscopeid()` extracts bytes 2-3 from link-local, multicast link-local, or site-local addresses into `sin6_scope_id` and clears those address bytes.

`inet6_putscopeid()` performs the inverse operation: it writes the scope ID back into bytes 2-3 in network order and clears `sin6_scope_id`. Without `__KAME__`, both functions compile to no-ops.
