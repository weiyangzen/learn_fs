# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsport.h

`nfsport.h` is the FreeBSD kernel portability and integration umbrella for the in-kernel NFS implementation. It pulls in kernel, network, VM, RPC, UFS, and NFS headers, then normalizes platform-specific types and operations behind NFS-specific macros.

Key contents:
- Defines port types such as `NFSSOCKADDR_T`, `NFSPROC_T`, `NFSDEV_T`, `NFSACL_T`, and vnode operation argument aliases.
- Provides mbuf allocation wrappers (`NFSMGET`, `NFSMGETHDR`, `NFSMCLGET`, `NFSMCLGETHDR`) that sleep/retry until allocation succeeds.
- Defines NFSv4 operation numbers, callback operation numbers, synthetic/stat-only operations, NFSv4.1/v4.2 operation counts, and NFS procedure numbers through `NFSV42_NPROCS`.
- Defines exported statistics ABI structures: `nfsstatsv1`, older `nfsstatsov1`, and legacy `ext_nfsstats`.
- Under `_KERNEL`, includes the core NFS common/client/server headers and adapts FreeBSD primitives for NFS code: credentials, vnode locking, socket addresses, signal masks, memory operations, monotonic time, malloc types, device numbers, vnode tags, and lock macros.
- Defines `struct nfsvattr`, mapping NFS attribute names onto FreeBSD `struct vattr` fields while adding NFS-specific supported attributes, mounted-on fileid, and filesystem id data.
- Defines NFSv4 server stable-storage records (`nfsrv_stablefirst`, `nfst_rec`, `nfsrv_stable`) and flags used during reclaim/grace handling.
- Defines many mount state helpers and predicates such as `NFSHASNFSV3`, `NFSHASNFSV4`, `NFSHASPNFS`, `NFSHASFLEXFILE`, `NFSHASTLS`, and write-verifier/session flags.
- Provides client request wrapper `struct nfsreq`, directory block size selection, delegation eligibility macro `NFSVNO_DELEGOK`, and MDS session helpers for pNFS.

Important integration points:
- This header is intentionally broad and central; almost every in-kernel NFS file depends on its macro layer.
- Its statistics structures are ABI-sensitive because userland tooling can consume them.
- Locking macros map NFS subsystem locks to FreeBSD `struct mtx` instances and encode expected lock ownership patterns.
- Some procedure definitions overlap with `nfsproto.h`, guarded by preprocessor checks, so consumers must preserve include ordering assumptions.

Research notes:
- This file is less protocol specification than FreeBSD binding layer. It bridges generic NFS code to FreeBSD vnode, VM, socket, mbuf, mount, and credential facilities.
- Changes here can have large blast radius because it defines operation numbering, stats array sizes, lock names, malloc tags, mount-state interpretation, and function prototypes used throughout client and server code.
