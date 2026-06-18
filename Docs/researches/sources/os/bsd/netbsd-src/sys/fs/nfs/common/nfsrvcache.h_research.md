# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvcache.h

This header defines the server recent-request cache used to detect duplicate NFS RPC requests and either drop, replay, or execute them. It provides cache sizing constants, the cache record layout, result flags, return codes, and bucket structure for fine-grained TCP cache locking.

Key contents:
- Cache sizing constants: `NFSRVCACHE_MAX_SIZE`, `NFSRVCACHE_MIN_SIZE`, and hash size `NFSRVCACHE_HASHSIZE`.
- `struct nfsrvcache`, with hash-chain links, ACK hash-chain links, UDP LRU link, RPC XID, completion timestamp, reply mbuf or reply status, UDP host address or TCP connection metadata, procedure number, and flags.
- Macros mapping union fields to readable names, including `rc_reply`, `rc_status`, `rc_haddr`, `rc_sockref`, `rc_tcpseq`, `rc_refcnt`, `rc_reqlen`, `rc_cksum`, `rc_cachetime`, and `rc_acked`.
- TCP ACK state constants `RC_NO_SEQ`, `RC_NO_ACK`, `RC_ACK`, and `RC_NACK`.
- Cache lookup/action return constants `RC_DROPIT`, `RC_REPLY`, and `RC_DOIT`.
- Entry flags for lock/wait state, reply representation, UDP/IP version, in-progress status, NFS protocol version, refcounting, and same-TCP-connection matching.
- `LIST_HEAD(nfsrvhashhead, nfsrvcache)` and `struct nfsrchash_bucket` with per-bucket mutex and list.

Important behavior:
- Cache entries can store either a full reply mbuf chain or a compact reply status. Callers must honor `RC_REPMBUF` versus `RC_REPSTATUS`.
- The structure handles UDP duplicate suppression and TCP request/ACK tracking in one record, using different union fields depending on transport.
- `RC_INPROG`, `RC_LOCKED`, and `RC_WANTED` support synchronization around duplicate requests while the first instance is still being processed.

Research notes:
- This file is the map for reading `nfs_nfsdcache.c`; the implementation must maintain flags and union interpretation consistently.
- Security and correctness review should focus on XID/address/connection matching, reply mbuf lifetime, refcount handling, and duplicate non-idempotent operation handling.
