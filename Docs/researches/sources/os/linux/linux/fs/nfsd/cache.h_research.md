# File Research: sources/os/linux/linux/fs/nfsd/cache.h

Defines the NFSD duplicate request/reply cache interface and cache-entry structure.

Key behavior:
- Defines `struct nfsd_cacherep`, keyed by XID, request checksum, procedure, protocol, version, request length, and peer address.
- Stores entries in both an rb-tree node and LRU list.
- Tracks cache entry state (`RC_UNUSED`, `RC_INPROG`, `RC_DONE`), reply type, secure-port status, timestamp, and either a reply buffer vector or status value.
- Defines cache lookup outcomes: `RC_DROPIT`, `RC_REPLY`, and `RC_DOIT`.
- Defines cache types: no-cache, status reply, and buffered reply.
- Sets cache expiration to 120 seconds and request checksum length to 256 bytes.
- Declares slab lifecycle, per-net reply cache lifecycle, lookup/update, and stats display helpers.

Important interactions:
- Used by NFSD procedure dispatch to detect duplicate non-idempotent RPCs and replay cached replies safely.
- `sockaddr_in6` is used intentionally for compact address storage.
