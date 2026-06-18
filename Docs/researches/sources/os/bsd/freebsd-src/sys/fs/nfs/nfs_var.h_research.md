# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_var.h

This is the broad internal prototype header for FreeBSD’s shared NFS client/server implementation. It forward-declares NFS structures and publishes cross-file function interfaces for server state, server RPC dispatch, duplicate request cache, common mbuf/attribute helpers, client RPC operations, client state management, VFS-port routines, and kernel RPC transport glue.

Key behavior:
- Forward-declares shared NFS types such as mounts, request descriptors, file handles, client/server state objects, sessions, layouts, device info, vattrs, and service argument structures.
- Groups prototypes by implementation file, making module boundaries explicit.
- Exposes NFSv4 server state control from `nfs_nfsdstate.c`: client/session creation and destruction, opens, locks, delegations, layout operations, stable storage, pNFS device IDs, and recovery/reclaim handling.
- Exposes server operation handlers from `nfs_nfsdserv.c` for NFSv3/v4 procedures, including ordinary vnode operations, sessions, pNFS, copy/clone/seek, and extended attributes.
- Exposes server socket/cache entry points from `nfs_nfsdsocket.c` and `nfs_nfsdcache.c`.
- Exposes shared helpers from `nfs_commonsubs.c`: request start, XDR/string/file-handle helpers, NFSv4 attributes, common locks, nfsuserd/id-name mapping, session sequencing, pNFS mirror lookup, ext-page mbuf growth, and destroy-session RPC.
- Exposes client-side common parsing and request helpers from `nfs_clcomsubs.c`.
- Exposes server-side vnode/attribute/file-handle helpers from `nfs_nfsdsubs.c`, `nfs_commonport.c`, `nfs_commonacl.c`, and `nfs_nfsdport.c`.
- Exposes client RPC functions from `nfs_clrpcops.c` for metadata, I/O, directory, locking, ACL, session, pNFS, copy/clone/seek, and xattr operations.
- Exposes NFSv4 client state management from `nfs_clstate.c`: opens, locks, delegations, client/session recovery, layout/device lifetime, renew thread behavior, and close/delegation return.
- Exposes client port/VFS glue from `nfs_clport.c`, client initialization, bio flush, node cache invalidation, common kernel RPC, server krpc, and callback daemon entry points.

Important interactions:
- This header is the main compile-time coupling point between NFS protocol code, VFS-port code, client state code, server state code, and transport code.
- It relies on types and macros from other NFS headers such as `nfsport.h`, `nfsdport.h`, `nfsclstate.h`, and protocol constant headers.
- The prototypes reflect FreeBSD-specific vnode, mount, thread, credential, and mbuf interfaces while preserving some portable naming conventions inherited from the multi-platform NFS code.

Edge cases:
- Because this is a central header, signature changes here imply broad rebuild and coordination across client, server, pNFS, and callback code.
- Many functions carry `NFSPROC_T *`, `struct ucred *`, and `struct nfsrv_descript *` parameters; callers must preserve protocol version, credential, and descriptor state correctly across layers.
