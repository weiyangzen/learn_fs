# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname_r.c

Reentrant service lookup by service name and optional protocol. `getservbyname_r()` opens service state with `setservent_r()`, searches with `_servent_getbyname()`, and closes the backing store unless `_SV_STAYOPEN` is set.

The implementation supports both compiled CDB service data and plain `/etc/services` parsing. The CDB path builds a length-prefixed key from `name` and `proto`, validates returned record bounds, checks aliases/name entries, and delegates record decoding to `_servent_parsedb()`. The plain-file path iterates `_servent_getline()` / `_servent_parseline()`, matches the canonical service name or aliases, and then applies the protocol filter.
