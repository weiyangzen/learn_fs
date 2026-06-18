# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsport.h

This header is the NetBSD porting and compatibility layer for the imported FreeBSD "newnfs" code. It centralizes kernel includes, type aliases, operation/procedure numbering, statistics ABI, memory allocation tags, locking macros, socket-address helpers, vnode helpers, and mount-state flag accessors so the common NFS implementation can mostly use FreeBSD-oriented names while compiling in NetBSD.

Key contents:
- Defines NetBSD-specific NFS type aliases such as `NFSSOCKADDR_T`, `NFSPROC_T`, `NFSDEV_T`, `NFSACL_T`, and VOP argument aliases used by common client/server code.
- Provides mbuf allocation wrappers `NFSMGET`, `NFSMGETHDR`, `NFSMCLGET`, and `NFSMCLGETHDR`, with retry/catnap behavior on allocation failure.
- Defines NFSv4 and NFSv4.1 operation numbers, callback operation numbers, fake operation numbers for statistics, and synthetic NFSv4 procedure numbers used by the implementation.
- Defines `struct nfsstatsv1`, the newer 64-bit stats ABI with per-RPC, server operation, callback, cache, state-object, byte, operation-count, and duration counters. It also preserves `struct ext_nfsstats` for older 32-bit statistics consumers.
- Pulls together common NFS headers when `_KERNEL` is set, including `nfskpiport.h`, `nfsdport.h`, `rpcv2.h`, `nfsproto.h`, client/server state headers, XDR helpers, and mount/node headers.
- Defines NetBSD-facing attribute wrapper `struct nfsvattr`, mapping `na_*` names onto `struct vattr` fields while adding NFSv4 supported-attribute and filesystem identity fields.
- Defines server stable-storage restart structures (`nfsrv_stablefirst`, `nfst_rec`, `nfsrv_stable`) and flags used by NFSv4 reclaim/grace handling.
- Maps common NFS locks to NetBSD mutex calls: state, request, socket, name-id, client-state, nfsd, vnode node, mount, request, data-server, and session locks.
- Declares NetBSD malloc types and maps generic NFS allocation names such as `M_NFSDSTATE`, `M_NFSCLOPEN`, `M_NFSLAYOUT`, and `M_NFSSOCKREQ`.
- Defines NetBSD mount state bits and macros such as `NFSHASWRITEVERF`, `NFSHASPNFS`, `NFSHASNFSV4N`, `NFSSTA_LOCKTIMEO`, `NFSSTA_SESSPERSIST`, and `NFSSTA_PNFS`.
- Provides vnode/cache helpers, directory block sizing, `vn_rdwr` wrapper macro, file-size limits, device number conversion, attribute-cache invalidation, vnode lock wrappers, and NFS request structure definition.

Important behavior:
- This file is not protocol-marshalling code itself; it is the glue that makes common NFS client/server source portable across BSD kernels.
- The stats arrays are sized by protocol constants from the same header. Changes to NFSv4 operation counts, fake ops, or callback operation counts affect the ABI and every stats consumer.
- Locking macros define the expected lock order and concrete mutex types used throughout the NFS common, client, server, pNFS, and NLM paths.
- Mount state bits include pNFS and session flags in high bits of `nm_state`; collisions with NetBSD mount or NFS flags would be serious.
- The file keeps compatibility with imported FreeBSD comments and structures while adding NetBSD-specific replacements such as `time_uptime`, `vfs_statfs(m)`, and `NFS_DIRBLKSIZ`.

Research notes:
- This is the first file to inspect when resolving compile portability, lock primitive, allocator, stat ABI, or NetBSD-vs-FreeBSD semantic mismatches in the new NFS stack.
- Risk areas are macro side effects, duplicated operation/procedure constants also present in `nfsproto.h`, statistics ABI sizing, and lock macros that hide concrete mutex requirements.
