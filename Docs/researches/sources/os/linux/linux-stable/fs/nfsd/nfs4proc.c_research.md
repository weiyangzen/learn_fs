# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4proc.c

Purpose: implements the NFSD NFSv4 server procedure layer: the NULL and COMPOUND RPC procedures, most NFSv4 operation handlers, NFSv4.2 server-side copy/offload support, pNFS operation glue, reply size estimation, operation ordering checks, and the operation descriptor table.

Key structures and state:
- The central runtime object is `struct nfsd4_compound_state`, populated for each COMPOUND with current/saved filehandles, current/saved stateids, client/session state, and replay state.
- Operation handlers consume `union nfsd4_op_u` fields decoded by XDR code and return NFS status codes.
- `nfsd4_ops[]` maps each NFSv4 op number to handler, release hook, flags, reply size estimator, stateid getter/setter hooks, and operation name.
- Async NFSv4.2 COPY state is managed by `struct nfsd4_copy` entries on per-client `async_copies`, with flags for completed/stopped/offload callback state.

Major logic:
- Attribute validation is centralized in `check_attr_support()`, including ACL, POSIX ACL, security label, writable-mask, and `MODE_UMASK` conflict checks.
- OPEN handling implements NFSv4 create/open claim semantics, sequence/replay behavior, grace-period checks, reclaim checks, exclusive verifier handling, permission checks, delegation claim handling, and final state creation via state-layer helpers.
- Filehandle ops (`PUTFH`, `PUTROOTFH`, `SAVEFH`, `RESTOREFH`, `GETFH`, lookup variants) maintain current/saved handles and preserve current stateid where required.
- VFS-backed ops include access, commit, create, getattr, link, read, readdir, readlink, remove, rename, setattr, write, verify/nverify, xattrs, allocate/deallocate, clone, seek, and read-plus dispatch through read.
- SETATTR handles size changes and delegated attribute updates with stateid validation; delegated time attributes are vetted against delegation timestamps and current inode time.
- WRITE validates offset bounds, preprocesses write stateid, marks write-attrs delegations as written, calls `nfsd_vfs_write()`, and returns verifier/stability data.
- NFSv4.2 COPY supports intra-server copy and optional inter-server server-side copy. Async copy uses a kernel thread, per-net pending limits, callback stateid allocation, `CB_OFFLOAD`, offload status, and offload cancel.
- Inter-server copy support mounts the source server internally via NFS when `CONFIG_NFSD_V4_2_INTER_SSC` is enabled and the module parameter allows it.
- pNFS handlers validate layout type support, handle `GETDEVICEINFO`, `LAYOUTGET`, `LAYOUTCOMMIT`, and `LAYOUTRETURN`, and call layout driver operations plus `nfs4layouts.c` bookkeeping.
- `nfsd4_proc_compound()` drives execution: initializes response, validates minor version and NFSv4.1 operation ordering, clears deferral, iterates operations, checks filehandle/migration/wrongsec constraints, preflights reply size for non-idempotent operations, invokes handlers, updates current stateid, encodes replies, handles replay, and updates stats.
- Reply size helpers estimate maximum encoded response space for each op so mutating operations are not executed if their success reply cannot be encoded.
- `nfsd_version4` exposes the RPC version with NULL and COMPOUND procedures.

Concurrency and lifetime:
- Async copy lifecycle is protected by `clp->async_lock`, per-net client locks during cancellation scans, reference counts on copy objects, and explicit `nfsd_file` references.
- COMPOUND processing clears `RQ_USEDEFERRAL` to avoid non-idempotency problems.
- Operation release hooks release per-op resources such as read file references, lock denial owners, secinfo exports, layout buffers, and getdeviceinfo buffers.
- Client shutdown and superblock teardown can cancel active async copies safely.

Important dependencies:
- Delegates stateful open/lock/session/clientid operations to `nfs4state.c` through externally declared handlers referenced in `nfsd4_ops[]`.
- Uses `nfs4idmap.c` indirectly through attribute encode/decode paths for owner/group names.
- Uses `nfs4layouts.c` for pNFS layout state and `nfs4callback.c` for async offload callbacks.
- Uses VFS helper layer from `vfs.h`, ACL conversion from `acl.h`, current-stateid helpers, tracepoints, and per-net NFSD state.

Risk/edge cases:
- OPEN is specially handled when XDR decoding fails with a seqid-mutating error so the openowner seqid can still be advanced.
- Non-idempotent operations are guarded by reply size preflight; failures here prevent performing changes whose success could not be encoded.
- COPY async error handling intentionally reports success if bytes were written and lets clients query completion/error state later.
- Inter-server copy can mark saved source filehandles as foreign to tolerate stale local verification for COPY compounds.
- Grace-period checks differ for opens, locks/layout commits, and reclaim paths.
