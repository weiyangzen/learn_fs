# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs.h

## Summary
Defines private kernel-facing NFS client macros, debug controls, NFS I/O daemon state, and prototypes for client metadata, buffer I/O, RPC, commit, cache, node-locking, and initialization routines.

## Main Responsibilities
- Provide default terminal printf delay constants for NFS user-visible wait messages.
- Define mount-version predicates `NFS_ISV3`, `NFS_ISV4`, and `NFS_ISV34`.
- Define conditional NFS debug categories and the `NFS_DPF` debug-print macro.
- Define `enum nfsiod_state` for async I/O daemon availability and creation state.
- Declare core NFS client functions for sizing, direct writes, buffered reads/writes, buffer invalidation, async I/O dispatch, RPC reads/writes/readdir/readdirplus/readlink, commit handling, mount fsinfo, hash/node lifecycle, node locks, attribute cache lookup, and nfsiod creation.

## Key Interfaces
- Macros: `NFS_TPRINTF_INITIAL_DELAY`, `NFS_TPRINTF_DELAY`, `NFS_ISV3`, `NFS_ISV4`, `NFS_ISV34`, and `NFS_DPF`.
- Debug bits under `NFS_DEBUG`: `NFS_DEBUG_ASYNCIO`, `NFS_DEBUG_WG`, and `NFS_DEBUG_RC`.
- `enum nfsiod_state`.
- Prototypes including `ncl_bioread`, `ncl_biowrite`, `ncl_asyncio`, `ncl_doio`, `ncl_readrpc`, `ncl_writerpc`, `ncl_readdirrpc`, `ncl_readdirplusrpc`, `ncl_commit`, `ncl_fsinfo`, `ncl_init`, and `ncl_uninit`.

## Risks
This header is compiled only for `_KERNEL` and assumes surrounding NFS types such as `struct nfsmount` and `struct nfsnode` are available from other headers. Version macros dereference `v_mount` and `VFSTONFS()` without local validation. Debug output is compiled away unless `NFS_DEBUG` is set, so side effects must never be embedded in `NFS_DPF` arguments.
