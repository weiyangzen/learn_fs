# File Research: sources/local-fs/linux-apfs-rw/super.c

## Purpose

`super.c` implements APFS filesystem registration, mount and unmount handling, shared container state, superblock/checkpoint discovery, volume superblock and omap/catalog setup, mount option parsing, feature checks, inode cache setup, statfs, sync/remount operations, and block-device management.

## Container And Volume State

The file maintains a global `nxs` list of mounted APFS containers protected by `nxs_mutex`. A single container info object can be shared by multiple mounted volumes or snapshots. The mutex protects container lookup, reference counts, volume lists, shared omap references, first-mount flag selection, and backup superblock update coordination.

Each mounted volume gets an `apfs_sb_info`, while the shared container uses `apfs_nxsb_info`. The volume superblock uses a fake anonymous device for stat identity but reports the actual block device in mount info.

## Superblock Discovery

`apfs_read_main_super()` first reads the backup container superblock at block zero to learn the real block size, then scans the checkpoint descriptor area for the newest valid APFS NX superblock by magic, xid, and checksum. It rejects non-contiguous checkpoint descriptor trees and applies an arbitrary descriptor loop bound.

After selecting the checkpoint, it copies the NX superblock into memory, records block size and xid, sets the transaction buffer limit from RAM size, checks container features, and validates fusion UUIDs when applicable.

`apfs_make_super_copy()` writes the current checkpoint superblock back to block zero on final writable unmount of the container.

## Volume Mapping

`apfs_map_volume_super()` resolves the requested volume number through the container omap. It CoWs the container omap when writing, reads the omap root, looks up the volume superblock block, and maps it with `apfs_map_volume_super_bno()`.

`apfs_read_omap()` maps the volume omap object and root node, updating on-disk oids when CoW moves objects during write transactions. `apfs_first_read_omap()` shares a single omap object across the live volume and its snapshots. `apfs_read_catalog()` reads the catalog root through the volume omap.

Snapshot mounting maps the live volume and omap first, then calls `apfs_switch_to_snapshot()` to replace the volume superblock with the snapshot superblock before reading the snapshot catalog.

## Mount Lifecycle

`apfs_mount()` or `apfs_get_tree()` parses options, forces snapshot mounts read-only, attaches or creates shared container state with `apfs_attach_nxi()`, uses `sget()`/`sget_fc()` to reuse existing matching volume/snapshot superblocks, reads the main container superblock, and calls `apfs_fill_super()` for new superblocks.

`apfs_fill_super()` sets up backing-dev info, applies container flags, maps the volume, checks volume features, initializes/shared omap, optionally switches to a snapshot, reads the catalog, sets VFS operations, loads private and root inodes, creates the root dentry, and schedules orphan cleanup on writable mounts.

`apfs_put_super()` cancels cleanup/commit work, starts a sync transaction on writable unmount, updates modified-by software info and unmount time, forces commit, updates the backup superblock copy, and releases catalog, omap, and volume-super resources.

`apfs_kill_sb()` temporarily switches `s_dev` to the anonymous device before `kill_anon_super()`, then frees APFS superblock info and shared container references.

## Options And Feature Checks

Supported mount options include `readwrite`, `cknodes`, `uid=`, `gid=`, `vol=`, `snap=`, and `tier2=`. The first mount of a container decides container-wide flags; later incompatible flag requests are ignored with a warning.

Write support is deliberately gated behind `readwrite` or `CONFIG_APFS_RW_ALWAYS`, with warnings that it is experimental. Snapshots are always mounted read-only. Remount support only turns a volume read-only.

Container feature checks reject unknown incompatible features, enforce fusion tier2 requirements, and block writable fusion mounts. Volume feature checks reject unsupported encryption/restore/PFK/secondary-root cases, restrict writes for dataless snapshots and sealed volumes, warn on encrypted or preallocated-extent features, and reject unknown read-only-compatible features for writable mounts.

## VFS Integration

The file defines `apfs_sops`, inode allocation/destruction via a slab cache, `apfs_write_inode()` transaction wrapping, `apfs_statfs()` using shared container block counts and volume object counts, `apfs_sync_fs()` forced transaction commit, and filesystem registration through `apfs_fs_type`.

Kernel-version compatibility branches cover block-device open APIs, fs_context APIs, owner checks elsewhere, BDI APIs, dentry operation setup, and inode cache allocation.

## Invariants And Risks

- Container state is shared and reference-counted across volumes and snapshots.
- `nx_big_sem` serializes APFS filesystem writes and protects mount-time reads from concurrent CoW.
- The first mount controls container-wide checksum/write flags.
- The selected checkpoint is the highest-xid valid descriptor superblock.
- Writable unmount must force a transaction commit before updating the backup superblock.
- Error handling is conservative: aborted transactions force the container read-only.
- Fusion support is partial, and writable fusion mounts are blocked.

## Test Focus

Test multi-volume and multi-snapshot mounts, duplicate mount reuse, read-only mismatch rejection, checkpoint scanning with corrupt/newer descriptors, option parsing on old and fs_context kernels, feature-mask rejection, snapshot read-only forcing, writable unmount commit, backup superblock update, shared omap reference cleanup, statfs before/after spaceman load, and block-device cleanup on mount failures.
