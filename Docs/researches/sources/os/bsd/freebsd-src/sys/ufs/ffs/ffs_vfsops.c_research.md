# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vfsops.c

## Role

Implements the FreeBSD VFS operations for the `ufs` filesystem when backed by FFS. It owns mount, remount, unmount, sync, statfs, vnode lookup by inode/file handle, superblock update, device strategy integration, initialization, and teardown.

## Main Responsibilities

- Registers `ufs_vfsops` with the VFS layer.
- Mounts FFS filesystems from GEOM-backed disk vnodes.
- Handles mount updates, including read-only/read-write transitions and snapshot requests.
- Loads and validates superblocks through `ffs_sbget()` / `ffs_sbsearch()`.
- Constructs and tears down `struct ufsmount`.
- Sets feature flags for ACLs, NFSv4 ACLs, MAC multilabel, TRIM, soft updates, gjournal, and untrusted mounts.
- Reloads in-core filesystem state after fsck or write suspension.
- Flushes vnodes, quotas, snapshots, softdep work, TRIM work, device buffers, and superblocks.
- Implements inode-to-vnode and file-handle-to-vnode lookup.
- Maintains UMA zones for inodes and UFS1/UFS2 dinodes.
- Provides custom FFS buffer operations and GEOM strategy glue.
- Initiates forced unmount cleanup when media disappears with `ENXIO`.

## VFS Registration

`ufs_vfsops` supplies:

- `vfs_mount`: `ffs_mount`
- `vfs_cmount`: `ffs_cmount`
- `vfs_unmount`: `ffs_unmount`
- `vfs_statfs`: `ffs_statfs`
- `vfs_sync`: `ffs_sync`
- `vfs_vget`: `ffs_vget`
- `vfs_fhtovp`: `ffs_fhtovp`
- `vfs_extattrctl`: `ffs_extattrctl`
- `vfs_susp_clean`: `process_deferred_inactive`
- root handling through `vfs_cache_root` / `ufs_root`

The module is registered as `ufs` and uses FFS-specific vnode and buffer operations.

## Mount Path

`ffs_mount()` parses options and handles three major cases:

- Snapshot requests: `MNT_SNAPSHOT` on an update mount calls `ffs_snapshot()`.
- New mounts: resolves the device vnode, checks access, then calls `ffs_mountfs()`.
- Update mounts: validates the same device, supports read-write to read-only, read-only to read-write, and reload operations.

`ffs_mountfs()`:

- Allocates a private mount device vnode with `mntfs_allocvp()`.
- Opens the provider through GEOM.
- Installs FFS buffer operations on the device vnode.
- Reads the superblock and summary info.
- Rejects unsafe dirty filesystems unless read-only, forced, or otherwise allowed.
- Allocates `struct ufsmount` and fills function pointers for allocation, truncate, update, valloc/vfree, read-only checks, and snapshots.
- Configures UFS1 versus UFS2 behavior.
- Enables untrusted block validation if requested.
- Sets mount fsid and local mount flags.
- Configures MAC, ACL, NFSv4 ACL, TRIM, and speedup capabilities.
- Starts soft updates when configured.
- Reattaches existing snapshots with `ffs_snapshot_mount()`.
- Marks the filesystem dirty on writable mounts and writes the superblock.

## Remount and Reload

Read-only transition:

- Suspends writes.
- Flushes files via softdep or ordinary FFS flush.
- Marks the filesystem clean if appropriate.
- Writes the superblock.
- Tears down soft updates and GEOM write access.
- Sets `MNT_RDONLY`.

Read-write transition:

- Checks device permissions.
- Rejects unclean filesystems unless forced or allowed by softdep/SUJ rules.
- Reopens GEOM write access.
- Suspends writes during transition.
- Starts soft updates if needed.
- Marks the filesystem dirty.
- Writes the superblock.
- Reattaches snapshots.

`ffs_reload()`:

- Requires read-only mount unless forced.
- Invalidates device metadata buffers.
- Re-reads the superblock.
- Replaces `ump->um_fs`.
- Optionally clears suspension flags for unsuspend.
- Iterates active vnodes, invalidates file data, and reloads inode contents from disk.

## Inode Loading and Validation

`ffs_load_inode()` copies UFS1 or UFS2 dinodes into `struct inode`.

- UFS1: copies legacy fields and applies timestamp compatibility fixes.
- UFS2: verifies dinode check hash before accepting the inode.
- Both paths update mode, nlink, size, flags, generation, uid, and gid.

`ffs_check_blkno()` is enabled for `MNT_UNTRUSTED` mounts. It verifies data block pointers are inside legal filesystem data regions and do not point into inode/superblock areas, except for zero and snapshot marker values.

## Failure Cleanup

`ffs_fsfail_cleanup()` and `ffs_fsfail_cleanup_locked()` handle `ENXIO` media-loss failures:

- Mark `UM_FSFAIL_CLEANUP`.
- Panic if the affected mount is root.
- Queue a forced deferred recursive unmount.
- Return whether cleanup is in progress.

`ffs_breadz()` wraps buffered reads and can synthesize zeroed buffers during cleanup so soft updates can unwind dependencies even when the device can no longer be read.

## Unmount and Flush

`ffs_unmount()`:

- Stops extended attributes.
- Suspends writes on writable mounts.
- Flushes through softdep or `ffs_flushfiles()`.
- Unmounts soft updates.
- Marks the filesystem clean when possible.
- Writes the final superblock.
- Resumes suspended writes.
- Drains TRIM queues.
- Closes GEOM, releases vnodes/devices, destroys locks, and frees mount/superblock memory.

`ffs_flushfiles()`:

- Flushes user vnodes.
- Turns off quotas.
- Detaches active snapshots and forces system vnode closure when snapshots were active.
- Waits for TRIM work to drain.
- Fsyncs the device vnode.

## Sync and Statfs

`ffs_statfs()` reports block and inode totals using superblock summary counts plus pending softdep blocks/inodes.

`ffs_sync_lazy()` handles access-time-only lazy syncs and superblock updates.

`ffs_sync()`:

- Iterates dirty vnodes and calls `ffs_syncvnode()`.
- Flushes softdep work for wait syncs.
- Fsyncs the device vnode.
- Coordinates `MNT_SUSPEND` by checking softdep and secondary write counters, then setting `MNTK_SUSPEND2 | MNTK_SUSPENDED`.
- Writes the superblock if modified.

## Vnode Lookup and File Handles

`ffs_vgetf()`:

- Uses the VFS inode hash.
- Allocates `struct inode` from UMA.
- Creates a vnode with UFS1 or UFS2 vnode operations.
- Reads or initializes the dinode.
- Loads softdep inode dependencies when needed.
- Calls `ufs_vinit()` to set vnode type and aliases.
- Generates a missing inode generation number for old filesystems.
- Associates MAC labels for multilabel mounts.
- Marks the vnode constructed.

`ffs_inotovp()` validates inode range, checks UFS2 lazy inode initialization, gets the vnode, and verifies mode, generation, and link count for NFS/file-handle safety.

`ffs_fhtovp()` maps `struct ufid` file handles to vnodes through `ffs_inotovp()`.

## Superblock Update Path

`ffs_sbupdate()` serializes superblock updates through the superblock buffer, copies the in-memory superblock into it, clears `fs_fmod`, and calls `ffs_sbput()` with `ffs_use_bwrite()`.

`ffs_use_bwrite()` writes summary blocks and the superblock, marks suspended-write buffers with `B_VALIDSUSPWRT`, integrates softdep superblock dependencies, and returns negative error encoding when the caller must not restore pointer fields.

## Buffer and GEOM Integration

`ffs_ops` installs:

- `ffs_bufwrite()` for custom buffer write behavior.
- `ffs_geom_strategy()` for direct GEOM I/O.
- `ffs_bdflush()` when snapshots are enabled.

`ffs_bufwrite()`:

- Supports background writes for buffers marked `BX_BKGRDWRITE`.
- Copies buffers for async background write so the original remains usable.
- Moves softdep dependencies to the copy.
- Updates cylinder group check hashes before release/write.
- Handles background write completion through `ffs_backgroundwritedone()`.

`ffs_geom_strategy()`:

- Bypasses `VOP_STRATEGY()` for private FFS device vnodes.
- Rejects unauthorized writes during suspension unless `B_VALIDSUSPWRT` is set.
- Runs `ffs_copyonwrite()` before writes when snapshots are active.
- Starts softdep dependencies before write I/O.
- Updates cylinder group CRCs for metadata buffers.
- Marks non-read I/O for ENXIO conversion when enabled.
- Submits the buffer to GEOM via `g_vfs_strategy()`.

## Research Relevance

This file is a broad map of how FFS plugs into FreeBSD VFS and GEOM. It is especially useful for studying mount lifecycle, filesystem trust validation, soft updates integration, snapshot write interception, buffer-cache policy, forced unmount on media loss, and vnode/inode instantiation.
