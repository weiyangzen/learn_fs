# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfraginfo.c

Fragment-cache entry printer.

Key behavior:
- Prints family, source, destination, fragment ID, TTL, protocol, packet/byte counters, seen-first-fragment flag, and refcount.

Research notes:
- Uses `hostname()` for address rendering.
