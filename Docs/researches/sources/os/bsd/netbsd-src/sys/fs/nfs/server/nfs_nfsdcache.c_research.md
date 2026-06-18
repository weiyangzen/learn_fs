# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdcache.c

Implements the NFS server duplicate request cache. The long file comment explains the design: false hits are worse than false misses, NFSv4 seqid ordering must not be broken, UDP uses the traditional xid/procedure/client cache, and TCP/NFSv4 uses stricter matching with request length/checksum, socket timing, and seqid references.

`nfsrvd_getcache()` allocates a request cache record and dispatches to UDP or TCP lookup. UDP keys on xid, NFS version, procedure, and client address, with an LRU list and in-progress suppression. TCP keys on xid/version/procedure plus request length/checksum and additional socket constraints, allowing multiple entries per key to avoid false hits.

`nfsrvd_updatecache()` decides whether to save a reply, return a cached reply for NFSv4 seqid handling, or free the entry. It saves status-only NFSv2 replies where possible and mbuf copies otherwise. `nfsrvd_sentcache()` records TCP reply sequence state after send, while `nfsrc_trimcache()` expires UDP/TCP entries by timeout, acknowledgment, final socket loss, high-water pressure, and refcount state.

Reference helpers `nfsrvd_refcache()` and `nfsrvd_derefcache()` pin cache entries for NFSv4 owner seqid sequencing. Cache entries are protected by per-bucket mutexes or the UDP mutex, with explicit `RC_LOCKED`/`RC_WANTED` entry locking. Sysctls control TCP high water, UDP high water, TCP timeout, and TCP non-idempotent caching.

Key dependencies are `struct nfsrv_descript`, mbuf copy/free APIs, NFS statistics, TCP acknowledgment hooks from the service transport, NFSv4 seqid code, and shared cache tables defined in `nfs_nfsdport.c`.
