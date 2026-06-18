# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clport.c

## Summary
FreeBSD-specific NFS client port layer. It ties generic newnfs client logic to FreeBSD vnode, mount, credential, pager, module, syscall, sysctl, Capsicum, and kernel-thread facilities.

## Main Responsibilities
- Creates and finds `nfsnode`/vnode instances by NFS file handle.
- Maintains NFS client attribute cache contents and pager size synchronization.
- Builds NFSv4 client IDs, open-owner names, and lock-owner names.
- Parses weak-cache-consistency and post-op attributes from NFS replies.
- Loads mount `statfs` and FSINFO-derived transfer-size limits.
- Maps NFSv4 protocol errors to local `errno` values.
- Implements client-side `nfssvc()` operations for callback sockets, callback nfsd workers, mount-option dumping, and forced dismount.
- Initializes and pins the `nfscl` kernel module.

## Key APIs
- `nfscl_nget()`, `nfscl_ngetreopen()`.
- `nfscl_loadattrcache()`, `ncl_copy_vattr()`, `ncl_pager_setsize()`.
- `nfscl_uuidcheck()`, `nfscl_fillclid()`, `nfscl_filllockowner()`, `nfscl_getparent()`.
- `nfscl_wcc_data()`, `nfscl_postop_attr()`, `nfscl_request()`.
- `nfscl_loadsbinfo()`, `nfscl_loadfsinfo()`.
- `newnfs_copyincred()`, `nfscl_checksattr()`, `nfscl_maperr()`, `nfscl_procdoesntexist()`.
- Internal syscall/module hooks: `nfssvc_nfscl()`, `nfscl_modevent()`.

## Important Behavior
`nfscl_nget()` uses `vfs_hash_get()`/`vfs_hash_insert()` keyed by an FNV hash of the file handle. It handles fake-root file handles, duplicate vnode races, doomed vnode checks, initial vnode construction, `VV_ROOT`, vnode operation switching for FIFOs, NFSv4.0 parent-fh/name side data, and loser vnode cleanup.

`nfscl_ngetreopen()` is a cache-only lookup variant used during reopen/recovery. It avoids blocking on vnode locks where possible because the caller holds exclusive client state.

`nfscl_loadattrcache()` rejects attribute updates where the server-reported fileid changes unexpectedly, rate-limits warnings, updates cached attributes, handles write-attribute partial refreshes, computes synthetic NFSv4 per-server-filesystem `va_fsid` values, reconciles local dirty size with server size, and invalidates stale attrs when mtime moves backwards.

`nfssvc_nfscl()` supports adding a callback socket with Capsicum socket rights, running callback service threads, copying formatted mount options to userland, and marking NFS mounts for forced dismount while canceling in-flight RPCs.

## State and Integration
Uses FreeBSD vnode/vfs hash tables, UMA zones, mount flags, NFS mount state, `nfsnode` locks, pager object size state, DTrace NFS probes, sysctls under `vfs.nfs`, and module dependencies on `nfscommon`, `krpc`, `nfssvc`, `xdr`, and `acl_nfs4`.

## Risks
VNode lifecycle is delicate: hash lookup/insert races, doomed vnode handling, `insmntque()` failure cleanup, lock state, and NFSv4 parent-name side data must stay consistent. Attribute-cache correctness depends on fileid stability, mtime ordering, local dirty-size rules, and pager size updates. Forced dismount and callback setup cross mount-list, data-server mirror, socket, and RPC cancellation state.
