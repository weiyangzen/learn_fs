# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vfsops.c

Implements NFSv3 client-side VFS operations: filesystem registration, mount argument import, mount setup, root vnode creation, unmount, statvfs, sync, vget, root mounting, and mount-info teardown.

Key elements:
- Static call metadata:
  - `rfsnames_v3[]` names NFSv3 procedures for stats.
  - `call_type_v3[]`, `timer_type_v3[]`, and `ss_call_type_v3[]` classify procedure timeout/retry behavior.
- `nfs3init()` registers NFSv3 VFS ops and vnode ops, stores `nfs3fstyp`, and reports template registration failures.
- `nfs3fini()` is empty; VFS-level init/fini is handled separately by `nfs3_vfsinit()` and `nfs3_vfsfini()`.
- `nfs3_free_args()` releases copied-in mount arguments: filehandle, `knetconfig`, hostname, server address, sync address, netname, and security data.
- `nfs3_copyin()` imports user `nfs_args` in native or 32-bit data models, copies transport strings, netbufs, root filehandle, hostname, legacy secure mount data, new `sec_data`, and failover linked-list pointer for `NFS_ARGS_EXTB`.
- `nfs3_mount()`:
  - Enforces mount privilege and directory mount point.
  - Supports remount validation, rejecting locking-mode changes.
  - Checks mountpoint busy state unless overlay is requested.
  - Builds a `servinfo` list, including failover servers.
  - Validates `NFSMNT_KNCONF`, transport strings, server address, and NFSv3 filehandle length.
  - Handles RDMA mount selection through `rdma_reachable()`, including `NFSMNT_TRYRDMA` fallback and `NFSMNT_DORDMA` server rejection.
  - Loads new or legacy security data, defaulting to AUTH_UNIX, and temporarily enables `AUTH_F_TRYNONE` for secure mount probing.
  - Restricts failover to read-only hard mounts, determines the target zone, applies labeled-system mount policy, rejects mounts into shutting-down zones, calls `nfs3rootvp()`, and applies mount options with `nfs_setopts()`.
  - Cleans up root vnode, server list, async/kstats, and mount info on errors.
- Tunables: `nfs3_dynamic`, `nfs3_max_threads`, `nfs3_bsize`, `nfs3_async_clusters`, and `nfs3_cots_timeo`.
- `nfs3rootvp()`:
  - Allocates and initializes `mntinfo_t`, default flags, timers, stats pointers, ACL procedure metadata, failover CV, server list, attribute cache timings, rnode list, async state, and zone reference.
  - Assigns a unique NFS device id and VFS fsid.
  - Normalizes `nfs3_bsize` to a page multiple.
  - Creates the root rnode with `makenfs3node()`.
  - Calls `FSINFO` on every server to validate root type and choose the minimum supported transfer/read/write sizes and max file size across failover replicas.
  - Starts the async manager thread, initializes mount kstats, fills root type if needed, and returns the root vnode.
- `nfs3_unmount()`:
  - Requires unmount privilege.
  - Forced unmount marks `VFS_UNMOUNTED`, disables async scheduling, stops the async manager, destroys rnodes, deletes kstats, and returns.
  - Normal unmount stops async workers with signal handling, flushes rnodes, checks for active rnodes, restores async limit on busy failure, then stops manager, destroys rnodes, and deletes kstats.
- `nfs3_root()` returns a fresh root vnode for the current server, rejects cross-zone access, handles stale-root signaling through `SV_ROOT_STALE`, and restores known root vnode type.
- `nfs3_statvfs()` obtains root vnode, sends `FSSTAT`, updates root attrs, maps NFSv3 byte/file stats into `statvfs64`, handles unknown `-1` block fields, and purges stale handles on failures.
- `nfs3_sync()` flushes dirty NFS files through `rflush()` unless called for attribute-only sync, serialized by `nfs3_syncbusy`.
- `nfs3_vget()` reconstructs a vnode from an NFSv3 filehandle fid, rejects oversized fids and wrong zones, fetches attributes for unknown type, and maps stale rnodes to `ENOENT`.
- `nfs3_mountroot()` handles NFSv3 root filesystem boot mounting. It calls `mount_root()`, builds `servinfo`, forces AUTH_UNIX, calls `nfs3rootvp()`, applies options, adds the VFS, and updates `rootfs.bo_name`.
- `nfs3_vfsinit()` initializes the sync mutex; `nfs3_vfsfini()` destroys it.
- `nfs3_freevfs()` releases server info and `mntinfo_t` after unmount, asserting kstats were already deleted.

Dependencies:
- illumos VFS/vnode registration and lifecycle: `vfs_setfsops`, `vn_make_ops`, `vfs_make_fsid`, `vfs_add`, `vfs_lock_wait`, `VFS_HOLD`, `VFS_RELE`, `vfs_devismounted`.
- NFS client internals: `mntinfo_t`, `servinfo_t`, `makenfs3node`, `rfs3call`, `nfs3_tsize`, `nfs3getattr`, `nfs_setopts`, `nfs_async_*`, `rflush`, `check_rtable`, `destroy_rtable`, `nfs_free_mi`, `nfs_mnt_kstat_init`.
- Security and zones: `secpolicy_fs_mount`, `secpolicy_fs_unmount`, `sec_clnt_loadinfo`, `sec_clnt_freeinfo`, `nfs_mount_label_policy`, `zone_find_by_path`, `zone_hold/rele`, `zone_hold_ref`, `nfs_mi_zonelist_add`.
- RDMA and transport support: `rdma_reachable`, `knetconfig`, `netbuf`, transport semantics/timeouts.
- Boot/root support: `mount_root`, `getfsname`, `rootfs`, `clkset`.

Research notes:
- Failover mounts use a server list and select conservative transfer sizes by taking minimum server-advertised limits.
- Mount setup is sensitive to ownership transfer from `nfs_args` into `servinfo`; `nfs3_free_args()` intentionally nulls fields after transfer.
- There is a suspicious legacy AUTH_DES setup line copying `knc_proto` into `pf` instead of `p`; this report records the observed code and does not change it.
