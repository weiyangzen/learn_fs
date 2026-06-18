# File Research: sources/os/linux/linux-stable/fs/jfs/super.c

## Purpose

Provides the JFS filesystem type integration: module setup/teardown, superblock operations, mount option parsing via `fs_context`, remount/reconfigure handling, freeze/unfreeze, quota file I/O, statfs, export ops, and inode-cache lifecycle.

## Mount And Context Handling

- `jfs_param_spec` accepts integrity/nointegrity, `iocharset`, remount-only `resize`, error behavior, quota options, uid/gid/umask, and discard settings.
- `jfs_parse_param()` updates a private `jfs_context`, loading/unloading NLS tables as needed.
- `jfs_init_options()` seeds defaults, with `errors=remount-ro` as the default behavior for new mounts.
- `jfs_fill_super()` allocates `jfs_sb_info`, sets VFS operations and xattr handlers, creates the direct-mapping inode for metadata I/O, mounts the aggregate, optionally mounts read-write/log state, obtains the root inode, and sets maxbytes/time granularity.
- `jfs_reconfigure()` applies parsed options, handles online resize, transitions read-only/read-write state, and remounts the log path if integrity mode changes.

## Super Operations

`jfs_super_operations` includes inode allocation/free, dirty/write/evict inode hooks, `put_super`, `sync_fs`, freeze/unfreeze, `statfs`, option display, and quota hooks when configured. `jfs_statfs()` reports block counts from the bmap and estimates inode capacity from current inode map plus available blocks.

## Error And Freeze Behavior

`jfs_error()` logs the caller and message, marks the superblock dirty through `updateSuper(FM_DIRTY)`, and then either panics, remounts read-only, or continues according to mount flags. Freeze quiesces transactions, shuts down the log, and marks the superblock clean; unfreeze marks mounted, reinitializes the log, and resumes transactions.

## Quota Support

Quota reads and writes bypass pagecache-level regular write paths by mapping quota-file logical blocks through `jfs_get_block()` and reading/writing buffers directly. `jfs_quota_on()` marks quota files noatime/immutable in JFS and VFS flags; `jfs_quota_off()` clears them after quota shutdown.

## Module Lifecycle

`init_jfs_fs()` creates the inode cache with usercopy bounds for inline inode data, initializes metapages and the transaction manager, starts the JFS I/O, commit, and sync kernel threads, initializes proc entries when enabled, and registers the filesystem. Exit reverses this sequence and runs `rcu_barrier()` before destroying the inode cache.

## Notes

The direct inode is fake-hashed and uses `jfs_metapage_aops` for aggregate metadata access. Discard is disabled at mount if the block device reports no discard support. JFS export operations use generic 32-bit inode file handles plus JFS parent lookup from `namei.c`.
