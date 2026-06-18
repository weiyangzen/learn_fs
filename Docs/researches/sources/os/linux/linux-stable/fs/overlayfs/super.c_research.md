# File Research: sources/os/linux/linux-stable/fs/overlayfs/super.c

## Purpose

`super.c` implements overlayfs filesystem registration, superblock setup, layer construction, work/index directory setup, mount-time feature probing, dentry/inode/super operations, and teardown.

## Main Responsibilities

- Register the `overlay` filesystem and allocate overlay inode cache.
- Implement overlay superblock operations.
- Define overlay dentry operations, including `d_real()` and revalidation.
- Validate and clone upper/lower mounts into private overlay mounts.
- Create and validate workdir/indexdir.
- Probe upper/lower filesystem capabilities.
- Build layer arrays, fsid mapping, xino mode, and root overlay inode.
- Select export operations for NFS/exportfs support.
- Enforce stacking-depth and overlapping-layer constraints.

## Dentry And Inode Operations

`ovl_d_real()` returns the real dentry for regular-file data or metadata, using lazy lowerdata verification for metacopy data paths. It recurses through stacked lower filesystems with `d_real()`.

`ovl_dentry_revalidate_common()` delegates revalidation/weak revalidation to all real upper/lower dentries attached to an overlay dentry.

`ovl_alloc_inode()`, `ovl_destroy_inode()`, and `ovl_free_inode()` manage `struct ovl_inode` state, including upper dentry refs, lower stacks, directory caches, redirect strings, and mutexes.

`ovl_super_operations` includes inode allocation/free/destruction, `inode_just_drop`, `put_super`, `sync_fs`, `statfs`, and `show_options`.

## Workdir And Upper Setup

`ovl_get_upper()` validates upperdir, checks namelen, creates a trap inode, clones a private upper mount, strips atime mount flags, inherits `SB_NOSEC`, and takes the in-use lock.

`ovl_get_workdir()` requires workdir and upperdir to be on the same mount and separate subtrees. It locks workbasedir, sets a trap, and calls `ovl_make_workdir()`.

`ovl_make_workdir()` creates/cleans `work/`, validates d_type, tmpfile support, `RENAME_WHITEOUT`, overlay xattr support, file-handle support, and volatile dirty markers. It downgrades features such as redirect, metacopy, index, UUID, and xino when upper capabilities are insufficient.

`ovl_get_indexdir()` turns `index/` into the active workdir when indexing is enabled, verifies root origin/upper xattrs, and invokes `ovl_indexdir_cleanup()`.

## Lower Layer And Fsid Setup

`ovl_lower_dir()` probes namelen, stack depth, file-handle support, and inode encoding. It can disable index/NFS/xino when lower filesystems cannot support required file-handle behavior.

`ovl_get_fsid()` assigns unique fsids to underlying superblocks, checks UUID conflicts, allocates pseudo devices, and marks UUID conflicts that disable file-handle decoding features.

`ovl_get_layers()` allocates fs records, reserves fsid 0 for upper, clones private lower mounts as read-only/noatime, assigns traps, assigns fsid/layer indexes, preserves lowerdir display strings, and validates encoding consistency.

`ovl_get_lowerstack()` validates lower counts, checks all lowers, enforces stack-depth limit, builds root lowerstack excluding data-only layers, and records `numdatalayer`.

## Root And Superblock Setup

`ovl_fill_super()` ensures the current user namespace matches the fs-context namespace, sets dentry operations, prepares creator credentials if needed, enters overlay credentials, and calls `ovl_fill_super_creds()`.

`ovl_fill_super_creds()` verifies options, allocates layers/config lowerdir array, initializes xino mode, sets super operations early for traps, sets up upper/work/lower/index state, checks overlapping layers, chooses export operations, lowers `CAP_SYS_RESOURCE`, sets superblock flags and xattr handlers, and creates the root dentry with `ovl_get_root()`.

`ovl_get_root()` creates a directory inode, chooses root ino/fsid from upper or top lower, marks root merge/whiteout/connected/upperdata flags, detects xwhiteout markers in lower roots, initializes inode state, and installs dentry flags.

## Export And Sync Behavior

If `nfs_export=on`, `sb->s_export_op` is `ovl_export_operations`. If all layers support file handles but NFS export is off, `ovl_export_fid_operations` is used for non-decodable handle support.

`ovl_sync_fs()` skips real sync on volatile clean mounts, otherwise syncs upper fs during wait phase.

## Risk Notes

- Mount setup contains many feature downgrades; reports in `/proc/mounts` reflect effective behavior, not necessarily requested behavior.
- Workdir cleanup and indexdir cleanup can delete stale internal entries and must never target user data outside validated work/index dirs.
- Overlapping layer traps prevent recursive/self-overlay corruption.
- UUID/fsid and xino decisions affect persistent inode identity and export correctness.
