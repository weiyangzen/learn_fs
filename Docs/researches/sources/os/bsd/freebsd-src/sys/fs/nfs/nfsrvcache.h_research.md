# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvcache.h

`nfsrvcache.h` defines the NFS server recent request cache used to detect duplicate RPC requests and replay/drop/execute them safely.

Key contents:
- Defines cache sizing bounds: `NFSRVCACHE_MAX_SIZE`, `NFSRVCACHE_MIN_SIZE`, and `NFSRVCACHE_HASHSIZE`.
- Defines `struct nfsrvcache`, with hash/list links, RPC xid, timestamp, cached reply mbuf or status, transport-specific identity, RPC procedure number, and state flags.
- Supports UDP identity via `union nethostaddr` and TCP/session-oriented identity via socket reference, request length, TCP sequence, checksum, cache time, ACK state, and refcount.
- Defines access macros for the nested reply/status/address/TCP fields.
- Defines ACK state values (`RC_NO_SEQ`, `RC_NO_ACK`, `RC_ACK`, `RC_NACK`) and cache action return values (`RC_DROPIT`, `RC_REPLY`, `RC_DOIT`).
- Defines cache flags for locking/waiting, cached reply type, transport, address family, in-progress state, NFS protocol version, reference count, and same-TCP-connection matching.
- Defines `LIST_HEAD(nfsrvhashhead, nfsrvcache)` and `struct nfsrchash_bucket`, a fine-grained locked TCP cache hash bucket.

Important integration points:
- This cache is server-side duplicate suppression and reply replay infrastructure.
- The same entry can represent either a full reply mbuf chain or only a reply status.
- Transport identity differs significantly between UDP and TCP, reflected by the `rc_un2` union.

Research notes:
- The header only defines data layout and constants; cache insertion, lookup, locking, replay, and eviction behavior live in server implementation files outside this group.
