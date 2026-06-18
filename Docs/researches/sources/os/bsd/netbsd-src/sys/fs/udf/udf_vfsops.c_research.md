# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vfsops.c

## Purpose

`udf_vfsops.c` implements NetBSD VFS operations for the UDF filesystem. It is the mount-level entry point that registers the filesystem, allocates/frees mount state, opens and closes the backing block device, performs mount-time UDF discovery through `udf_subr.c`, exposes root/stat/sync operations, and rejects unsupported VFS features.

## Module and VFS Registration

The file defines:
- `MODULE(MODULE_CLASS_VFS, udf, NULL)`.
- Global `udf_verbose` debug mask.
- UDF malloc types: `M_UDFMNT`, `M_UDFVOLD`, `M_UDFTEMP`.
- Global `udf_node_pool`.
- `udf_vnodeopv_descs`.
- `struct vfsops udf_vfsops`.

The `udf_vfsops` table wires:
- Mount lifecycle: `udf_mount`, `udf_start`, `udf_unmount`, `udf_mountroot`.
- Accessors: `udf_root`, `udf_statvfs`.
- Sync: `udf_sync`.
- Vnode cache integration: `udf_vget`, `udf_loadvnode`, `udf_newvnode`.
- File handle operations: `udf_fhtovp`, `udf_vptofh`.
- Init/reinit/done: `udf_init`, `udf_reinit`, `udf_done`.
- Snapshot/extattr/suspend/rename lock hooks.

Unsupported or stubbed operations include quotas, fs-level fsync, root mount, NFS-style vget/file handles, and snapshots.

## Initialization and Teardown

`udf_init()`:
- Attaches malloc types.
- Initializes `udf_node_pool` sized for `struct udf_node`.

`udf_reinit()`:
- No-op.

`udf_done()`:
- Destroys `udf_node_pool`.
- Detaches malloc types.

`udf_modcmd()`:
- Attaches or detaches `udf_vfsops` on module init/fini.
- Returns `ENOTTY` for unknown module commands.

The file also creates a debug sysctl node under `vfs.udf`; when `UDF_DEBUG` is enabled, it exposes writable `verbose`.

## Mount State Freeing

`free_udf_mountinfo()` frees:
- Anchors.
- Primary/logical/unallocated/implementation/logical-integrity descriptors.
- Partition descriptors and unallocated/freed descriptors.
- Metadata unallocated descriptor.
- Fileset descriptor and sparing table.
- Late-allocation mapping buffers.
- VAT table.
- Mount mutexes.
- The `struct udf_mount`.

`udf_release_system_nodes()` releases retained system vnodes:
- VAT node.
- Metadata node.
- Metadata mirror node.
- Metadata bitmap node.

## Mount Flow

`udf_mount()` handles:
- Argument validation and `MNT_GETARGS`.
- Rejects `MNT_UPDATE` with `EOPNOTSUPP`.
- Verifies mount argument version.
- Resolves the device path with `namei_simple_user()`.
- Requires a block device with a valid bdev switch.
- Authorizes read/write mount access via kauth.
- Opens the device with `VOP_OPEN()`.
- Calls `udf_mountfs()` to read and validate the filesystem.
- On failure, releases system nodes, finishes disc strategy, frees mount state, closes the device, and releases the vnode.
- Registers the mount on the special device with `spec_node_setmountedfs()`.
- Sets statvfs metadata.
- For writable mounts, calls `udf_open_logvol()`. If logical volume open fails, it downgrades to read-only rather than failing the already-mounted filesystem.

The writable-open downgrade is explicitly marked with a FIXME because the mount has progressed too far to return the open error cleanly.

## Actual Filesystem Mounting

`udf_mountfs()` performs the real UDF discovery:
1. Invalidates stale device buffers with `vinvalbuf()`.
2. Initializes mount stat fields, fsid, name length, and `MNT_LOCAL`.
3. Allocates and initializes `struct udf_mount`.
4. Initializes `logvol_mutex`, `allocate_mutex`, and `sync_lock`.
5. Initializes the node rbtree.
6. Stores mount args and device vnode.
7. Calls `udf_update_discinfo()`.
8. Validates sector size:
   - Must be a power of two.
   - Sector sizes `>= 8192` are rejected as an implementation limit.
9. For writable mounts:
   - Requires recordable media.
   - Rejects full sequential media.
   - Rejects updating previous sessions.
10. Starts bootstrap disc strategy.
11. Reads anchors using `udf_read_anchors()`.
12. Reads VDS space with `udf_read_vds_space()`.
13. Stops bootstrap strategy.
14. Processes VDS with `udf_process_vds()`.
15. Starts selected final disc strategy.
16. Allocates late-allocation mapping buffers and node allocation descriptor copy space.
17. Sets mount block-size shifts.
18. Reads VDS support tables through `udf_read_vds_tables()`.
19. Requires logical volume integrity to be closed; otherwise asks for fsck and returns `EPERM`.
20. Reads root directories with `udf_read_rootdirs()`.

This function is the bridge between generic NetBSD VFS mount setup and UDF-specific format interpretation in `udf_subr.c`.

## Unmount Flow

`udf_unmount()`:
- Gets `struct udf_mount`.
- Optionally performs debug sanity checks.
- Flushes non-system vnodes with `vflush(..., SKIPSYSTEM)`.
- Calls `udf_sync(..., FSYNC_WAIT, ...)`.
- Flushes again to ensure no busy non-system vnodes remain.
- Calls `udf_close_logvol()` to close writable logical volume/session.
- Releases retained system nodes.
- Flushes all remaining vnodes; failure is considered panic-worthy for system vnodes.
- Finishes disc strategy.
- Synchronizes caches.
- Closes the backing device.
- Clears mountedfs association on the special vnode.
- Releases the device vnode with `vput()`.
- Frees UDF mount info.
- Clears `mp->mnt_data` and `MNT_LOCAL`.

## Root and Statvfs

`udf_root()`:
- Uses `fileset_desc->rootdir_icb`.
- Calls `udf_get_node()` to get the root node.
- Verifies `VV_ROOT`.
- Returns the root vnode.

`udf_statvfs()`:
- Fills block size, fragment size, I/O size, flags.
- Locks `allocate_mutex`.
- Calls `udf_calc_freespace()`.
- Reads file/directory counts from logical volume integrity implementation data.
- Sets available/reserved counts mostly to zero.
- Calls `copy_statvfs_info()`.

The comment notes read-only behavior around available block reporting.

## Sync

`udf_sync_writeout_system_files()`:
- Writes VAT if requested.
- Writes metadata and physical partition bitmaps if requested.
- Clears bitmap write flags when successful and requested.

`udf_sync()`:
- Returns immediately on read-only mounts.
- Skips autosync if another sync is already in progress.
- Sets `ump->syncing`.
- Calls `udf_do_sync()` for vnode/data sync.
- On `MNT_WAIT`, writes system files/bitmaps synchronously.
- Clears `ump->syncing`.

`udf_do_sync()` itself is implemented in `udf_subr.c`.

## Unsupported VFS Features

The file returns `EOPNOTSUPP` for:
- `udf_mountroot()`
- `udf_vget()`
- `udf_fhtovp()`
- `udf_vptofh()`
- `udf_snapshot()`

This means:
- UDF cannot be used as NetBSD root filesystem through this path.
- NFS/export-style stable file handle lookup is not implemented.
- Filesystem snapshots are not implemented.

## Dependencies

This file depends on:
- NetBSD VFS, vnode, mount, module, sysctl, kauth, specfs, genfs, buf, and block device APIs.
- UDF mount and descriptor structures from `ecma167-udf.h`, `udf_mount.h`, `udf.h`, `udf_subr.h`, and `udf_bswap.h`.
- UDF support functions implemented mostly in `udf_subr.c` and sibling UDF files.

## Notable Constraints and Risks

- `MNT_UPDATE` is not supported.
- Mount arguments have only basic validation beyond version.
- Writable mounts on unsupported media are rejected early, but failure to open the logical volume after mount discovery downgrades to read-only.
- Sector size support is capped below 8192 bytes.
- Dirty logical volume integrity blocks mount and requires fsck.
- File handle and snapshot operations are stubs.
- Unmount can panic if system vnodes fail to flush after system-node release.
