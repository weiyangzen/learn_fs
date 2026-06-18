# File Research: sources/os/linux/linux-stable/fs/nfsd/cache.h

Purpose: Declares NFSD duplicate request/reply cache structures and APIs.

Key responsibilities:
- Defines `struct nfsd_cacherep`, keyed by XID, checksum, procedure, protocol, version, request length, address, and privileged-source-port flag.
- Supports RB-tree lookup and LRU aging.
- Defines cache entry states: unused, in-progress, done.
- Defines lookup outcomes: drop, reply, do it.
- Defines cache payload types: no cache, reply status, reply buffer.
- Sets expiration and checksum length constants.
- Declares slab lifecycle, per-net cache init/shutdown, lookup/update, and stats show APIs.

Integration:
- Used by NFSD request dispatch/cache implementation in `nfscache.c`.
- Tied to SUNRPC service requests and NFSD net namespace state.

Risks and notes:
- Uses `sockaddr_in6` rather than `sockaddr_storage` to reduce entry size.
- Checksums only the first 256 bytes of request payload.
