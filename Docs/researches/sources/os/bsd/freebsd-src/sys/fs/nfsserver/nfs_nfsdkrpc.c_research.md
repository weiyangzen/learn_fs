# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdkrpc.c

## Purpose

Provides the KRPC-facing NFS server dispatch layer. It receives RPC requests from the FreeBSD RPC service pool, validates NFS version/procedure/authentication, constructs `struct nfsrv_descript`, invokes duplicate-reply/session caching, calls the core NFS RPC executor, sends replies, manages server sockets, and controls the main `nfsd` service lifecycle.

## Main Data and Tunables

Global/per-vnet state:
- `newnfs_nfsv3_procid[]`: maps old NFSv2 RPC procedure numbers to generic NFSv3-style procedure numbers.
- `nfsrvd_pool`: per-vnet RPC service pool.
- `nfsrv_numnfsd`: per-vnet count of active nfsd service processes.
- `nfsd_suspend_lock`: v4 root/suspend shared lock used around request processing.
- `nfsrvd_inited`: per-vnet one-time initialization flag.
- `nfsrv_zeropnfsdat`: pNFS-related zero-data buffer freed during termination.

Sysctls:
- `vfs.nfsd.nfs_privport`: require privileged client source ports for non-null NFS requests.
- `vfs.nfsd.server_min_nfsvers`: minimum served NFS version.
- `vfs.nfsd.server_max_nfsvers`: maximum served NFS version.

## RPC Dispatch Flow

`nfssvc_program(struct svc_req *rqst, SVCXPRT *xprt)` is the registered RPC service callback. It:
1. Sets the current vnet and initializes `struct nfsrv_descript`.
2. Validates NFS version/procedure:
   - NFSv2 procedures are mapped through `newnfs_nfsv3_procid[]`.
   - NFSv3 uses the request procedure directly.
   - NFSv4 accepts only `NFSPROC_NULL` and `NFSV4PROC_COMPOUND`.
3. Realigns the request mbuf and populates descriptor request pointers, caller address, transport address, procedure, and flags.
4. Enforces privileged-port policy for non-null requests, with rate-limited logging and `svcerr_weakauth()` on failure.
5. Obtains credentials and accepts only `AUTH_SYS` or Kerberos RPCSEC_GSS flavors.
6. Sets GSS integrity/privacy flags from the credential flavor.
7. For NFSv4 plus GSS, parses the exported GSS principal manually from the raw credential to avoid a `gssd` upcall.
8. Records TLS state from `xprt->xp_tls`, including verified certificate and certificate-user flags.
9. Associates MAC credentials when MAC is enabled.
10. Takes a shared reference on `nfsd_suspend_lock`, checks NFSv4 root export authorization, and calls `nfs_proc()`.
11. Releases the suspend lock, frees request mbufs/credentials, handles drop/decode/auth errors, sends the mbuf reply, and calls `nfsrvd_sentcache()` when the duplicate-reply cache returned a post-send entry.

Null RPCs bypass normal credential/cache/RPC execution and return an empty reply mbuf.

## Cache and Execution Flow

`nfs_proc(struct nfsrv_descript *nd, uint32_t xid, SVCXPRT *xprt, struct nfsrvcache **rpp)` connects request dispatch to duplicate-reply handling and actual NFS operation execution.

Important behavior:
- Marks stream transports with `ND_STREAMSOCK`; datagrams are identified by non-null `nd_nam2`.
- Drops NFSv2 UDP requests when `nfsrv_mallocmget_limit()` reports memory pressure, because NFSv2 lacks a useful resource-delay error.
- For NFSv2/v3 over stream sockets, sets `ND_SAMETCPCONN`.
- Stores retry xid, current TCP cache time, and transport socket reference in the descriptor.
- For NFSv4, parses minor version/tag data via `nfsd_getminorvers()`.
- For NFSv4.1, bypasses `nfs_nfsdcache.c` duplicate-reply lookup because replies are cached in session slots.
- For non-v4.1, calls `nfsrvd_getcache()` and then `nfsrc_trimcache()` with the transport ACK state.

If the cache returns `RC_DOIT`, the function calls `nfsrvd_dorpc()`:
- For NFSv4.1, it optionally copies the reply mbuf, calls `nfsrv_cache_session()` when `ND_HASSEQUENCE` is set, and substitutes a cached reply for `NFSERR_REPLYFROMCACHE`.
- For other versions, it maps `NFSERR_DONTREPLY` to `RC_DROPIT`, otherwise `RC_REPLY`, and calls `nfsrvd_updatecache()`.

The returned `rpp` value is the cache entry that must be finalized after the send path records the TCP reply sequence.

## Socket and Transport Lifecycle

`nfssvc_loss(SVCXPRT *xprt)` is registered for stream transports. On connection loss, it fetches the latest ACK state, enters the vnet, and calls `nfsrc_trimcache(..., final=1)` so TCP cache entries can be marked ACKed or NACKed.

`nfsrvd_addsock(struct file *fp)` accepts a userspace-provided socket from `nfssvc()`:
- reserves send/receive socket buffer space using `sb_max_adj`,
- creates a datagram or virtual-circuit RPC transport,
- steals the socket from userland by replacing file ops/data,
- assigns a monotonically increasing `xp_sockref`,
- registers NFSv2/v3/v4 service callbacks according to min/max version sysctls,
- registers `nfssvc_loss()` for stream transports.

The static `sockref` counter is local to this function and used by the duplicate-reply cache to distinguish TCP connections.

## nfsd Service Lifecycle

`nfsrvd_nfsd(struct thread *td, struct nfsd_nfsd_args *args)` is the server-side handler for the nfsd service loop. It:
- copies the configured Kerberos principal string,
- allows only the first nfsd process in a vnet to run the RPC pool,
- sets process flags and global/per-vnet nfsd counters,
- creates pNFS device IDs,
- registers GSS service names for NFSv2/v3/v4 when a principal is configured,
- applies service pool min/max thread counts,
- adjusts Getattr behavior for pNFS service mode,
- runs `svc_run(nfsrvd_pool)`,
- resets pNFS Getattr changes, clears GSS service names, decrements counters, calls `nfsrvd_init(1)`, and clears the AST flag on exit.

Extra nfsd processes beyond the first return without running another service pool.

`nfsrvd_init(int terminating)` initializes or tears down the per-vnet server pool under `NFSD_LOCK` discipline:
- On startup, it creates the `nfsd` service pool, disables the pool-level RPC duplicate cache with `sp_rcache = NULL`, and wires file-handle affinity callbacks `fhanew_assign` and `fhanew_nd_complete`.
- On termination, it clears the master process pointer, frees layout/device/backchannel state, closes the service pool, and frees `nfsrv_zeropnfsdat`.

## Integration Points

This file is the bridge among:
- KRPC transport APIs: `svc_reg()`, `svc_run()`, `svc_sendreply_mbuf()`, `svc_dg_create()`, `svc_vc_create()`, `SVC_ACK()`.
- Duplicate-reply cache: `nfsrvd_getcache()`, `nfsrvd_updatecache()`, `nfsrvd_sentcache()`, `nfsrc_trimcache()`.
- NFS operation execution: `nfsrvd_dorpc()`.
- NFSv4.1 sessions: `nfsrv_cache_session()`.
- NFSv4 root export/suspend coordination: `nfsv4_lock()`, `nfsv4_getref()`, `nfsv4_relref()`, `nfsvno_v4rootexport()`.
- RPCSEC_GSS, RPC-over-TLS, MAC framework, and file-handle affinity scheduling.

## Risks and Review Notes

Principal parsing is manual and depends on the exported GSS name layout. The code performs length checks before copying, but malformed credential coverage is important.

The privileged-port check casts the caller sockaddr through IPv4-compatible offsets and relies on IPv4/IPv6 port fields being at the same offset, as noted in the source comment.

`nfsrvd_init(1)` tears down pool resources but does not reset `nfsrvd_inited` in this file; lifecycle correctness depends on surrounding mount/service initialization rules.

The service path has many cleanup exits. Useful tests include weak-auth failures, non-privileged source ports, GSS principal extraction failure, TLS flag propagation, NFSv4 root export denial, `RC_DROPIT`, `NFSERR_DONTREPLY`, v4.1 session-cache replay, stream loss cleanup, and nfsd service restart/termination behavior.
