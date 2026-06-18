# File Research: sources/os/linux/linux/fs/ceph/super.c

CephFS filesystem registration, mount option parsing, superblock setup, client lifecycle, module cache lifecycle, forced unmount/reconnect, and global module parameters.

Major areas:
- Superblock operations: `ceph_put_super()`, `ceph_statfs()`, `ceph_sync_fs()`, `ceph_umount_begin()`.
- Mount option parsing: `ceph_mount_parameters`, source parsing for old and new syntax, monitor address parsing, and per-option validation.
- Mount option comparison/display: `compare_mount_options()` and `ceph_show_options()`.
- Client lifecycle: `create_fs_client()`, `destroy_fs_client()`, workqueue creation/destruction, global `ceph_fsc_list`.
- Slab/mempool setup: inode, cap, cap-snap, cap-flush, dentry, file, dir-file, MDS request, writeback pagevec pool, and subvolume metrics cache.
- Mount flow: `ceph_get_tree()`, `ceph_set_super()`, `ceph_compare_super()`, `ceph_setup_bdi()`, `ceph_real_mount()`, `open_root_dentry()`.
- Remount/reconfigure: `ceph_reconfigure_fc()`.
- Shutdown coordination: stopping blockers for MDS/OSD paths and `ceph_kill_sb()`.
- Module registration: `init_ceph()`, `exit_ceph()`, `ceph_fs_type`.

Mount parsing:
- Supports old source syntax `<mon>[,<mon>...]:[/path]`.
- Supports new syntax `name@fsid.fsname=/path` plus `mon_addr=`.
- Canonicalizes repeated/trailing slashes in server path.
- Validates size options against page size and Ceph max message limits.
- Handles feature-gated options for fscache, POSIX ACLs, and test dummy encryption.
- Default options include dcache, no copy-from, and async directory ops.

Mount/superblock sharing:
- New fs client is created before `sget_fc()`.
- Existing superblock can be reused only if client/mount options, fsid, sb flags, blocklist state, and mount state are compatible.
- `CEPH_OPT_NOSHARE` disables sharing.

Unmount behavior:
- `ceph_kill_sb()` pre-unmounts MDS client, flushes workqueues, syncs filesystem, waits for dirty folios, advances MDS stopping state, waits for blockers, kills anonymous superblock, cleans debugfs/fscache, then destroys fs client.
- Forced unmount aborts OSD requests, forces MDS unmount, and bumps `filp_gen`.

Module parameters:
- `disable_send_metrics`: custom setter wakes all mounted clients when metrics sending is re-enabled.
- `mount_syntax_v1` and `mount_syntax_v2`: read-only support indicators.
- `enable_unsafe_idmap`: allows idmapped mounts without required MDS feature support.

Dependencies:
- Heavy integration with libceph, MDS client, OSD client, debugfs, fscrypt, fscache, VFS fs_context API, and tracepoints.
