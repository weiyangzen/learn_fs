# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vfsops.c

## Purpose
Implements NFSv2 VFS operations for illumos: filesystem initialization, mount/remount, root vnode construction, unmount, statvfs, sync, fid-to-vnode lookup, NFS root mounting, and final VFS cleanup.

## Main Entry Points
- `nfsinit()` registers NFS vfsops and vnode ops.
- `nfs_mount()` copies and validates user/sysspace mount arguments, builds `servinfo` lists, handles failover/RDMA/security/zone/label policy, creates the root vnode, and applies mount options.
- `nfsrootvp()` allocates and initializes `mntinfo_t`, creates the NFS root rnode, probes server attributes and statfs transfer sizes, starts async manager support, and initializes mount kstats.
- `nfs_unmount()` handles normal and forced unmounts, async shutdown, rnode flushing/destruction, and kstat cleanup.
- `nfs_root()`, `nfs_statvfs()`, `nfs_sync()`, `nfs_vget()`, and `nfs_mountroot()` implement core VFS callbacks.
- `nfs_freevfs()` releases pathconf, server lists, and mount info after VFS teardown.

## Internal Mechanics
Mount argument handling is split between `nfs_copyin()` and `nfs_free_args()`. `nfs_copyin()` supports native and 32-bit user data models through `STRUCT_*` macros, copies transport config, netbufs, file handle, hostname, secure sync address/netname, optional pathconf, and `sec_data`. It transfers ownership of copied pointers into `servinfo` during mount setup.

`nfs_mount()` supports linked `nfs_args` failover lists only for read-only hard mounts. It can replace TCP/UDP transport with RDMA transport when `NFSMNT_TRYRDMA` or `NFSMNT_DORDMA` is requested. `NFSMNT_DORDMA` may discard non-RDMA-capable replicas or reject the mount if no usable server remains.

Security handling accepts newer `sec_data` via `NFS_ARGS_EXTA/B`, validates RPC flavors for sysspace mounts, and preserves legacy `NFSMNT_SECURE`/`NFSMNT_RPCTIMESYNC` AUTH_DES setup. Non-UNIX/loopback flavors get `AUTH_F_TRYNONE` during mount probing so initial GETATTR/STATFS can retry with AUTH_NONE.

`nfsrootvp()` establishes mount defaults: NFS program/version, procedure name/stat tables, call/timer type tables, ACL procedure tables, attribute cache bounds, hard/soft/semisoft/interrupt/directio flags, async queues, per-zone mount linkage, device/fsid assignment, and root vnode. It queries every replica with `RFS_STATFS` to derive minimum server transfer size.

Pathconf data is globally interned in `allpc` with reference counts so multiple mounts can share identical POSIX pathconf structures. Remount only updates pathconf and rejects locking-mode changes.

## Dependencies
Uses illumos VFS/vnode infrastructure, NFS rnodes and mount info, RPC client/security modules, RDMA reachability, zones, Trusted Extensions label policy, kstats, async NFS worker infrastructure, DNLC/rnode cache helpers, and NFSv2 XDR routines from `nfs_xdr.c`.

## Risks and Notes
- The pathconf intern table is a static global list; correctness depends on mount/remount/free paths maintaining refcounts.
- RDMA mount handling mutates `servinfo` transport ownership and has several failover paths where cleanup ordering matters.
- Legacy AUTH_DES conversion has delicate ownership of copied `knetconfig`, netbuf, and netname fields.
- NFS root mounting is special: it uses boot-time `mount_root()`, always sets AUTH_UNIX, and installs the root VFS manually.
