# File Research: sources/os/linux/linux/fs/hfsplus/super.c

## Role

Implements HFS+ superblock lifecycle, filesystem registration, mount/open of metadata objects, root creation, volume header commit/sync, statfs, remount/reconfigure checks, inode cache management, and teardown.

## Inode Loading and Writeback

- `hfsplus_system_read_inode()` reads system-file forks from the active volume header:
  - extents and catalog files get `hfsplus_btree_aops`;
  - allocation file gets `hfsplus_aops`;
  - startup and attributes files are read from their volume-header fork fields;
  - system inodes receive dummy `S_IFREG` mode so VFS open checks see a valid file type.
- `hfsplus_iget()` initializes HFS+ inode-private fields for new inodes, then either:
  - looks up user/root CNIDs in the catalog B-tree and calls `hfsplus_cat_read_inode()`, or
  - reads special system inodes from volume-header forks.
- `hfsplus_system_write_inode()` writes system inode fork state back to the volume header, marks the backup header dirty when sizes change, and writes associated B-trees under the correct nested lock class.
- `hfsplus_write_inode()` writes dirty extents first, then serializes user/root inodes to the catalog or system inodes to the volume header.
- `hfsplus_evict_inode()` truncates final pages, clears the VFS inode, and unlinks resource-fork inode relationships.

## Superblock Commit and Sync

- `hfsplus_commit_superblock()`
  - Under `vh_mutex` and `alloc_mutex`, copies `free_blocks`, `next_cnid`, `folder_count`, and `file_count` into the active volume header.
  - If `HFSPLUS_SB_WRITEBACKUP` is set, copies active header contents to the backup header and writes both primary and backup headers.
  - Uses `hfsplus_submit_bio()` to write the primary header at `part_start + HFSPLUS_VOLHEAD_SECTOR` and backup header at `part_start + sect_count - 2`.
- `hfsplus_sync_fs()`
  - For synchronous syncs, explicitly writes catalog, extents, optional attributes, and allocation-file mappings.
  - Commits the superblock and issues `blkdev_issue_flush()` unless `HFSPLUS_SB_NOBARRIER` is set.
- `delayed_sync_fs()` runs queued delayed superblock sync work and reports errors.
- `hfsplus_mark_mdb_dirty()` queues delayed sync work for writable mounts, using `dirty_writeback_interval * 10`.
- `hfsplus_prepare_volume_header_for_commit()` updates mount version, modify date, write count, clears the clean-unmount bit, and sets the inconsistent bit before commit.

## Mount and Root Setup

`hfsplus_fill_super()` performs mount setup:

- initializes allocation/header locks, delayed work, and work lock;
- loads default NLS, falling back from UTF-8 to default NLS when needed;
- temporarily switches to UTF-8 to locate the hidden directory;
- reads the HFS+ wrapper/volume header via `hfsplus_read_wrapper()`;
- validates volume version and caches total/free blocks, next CNID, file/folder counts, and data/resource clump blocks;
- checks filesystem size against sector and page-index limits;
- installs `hfsplus_sops` and `MAX_LFS_FILESIZE`;
- forces read-only for unclean, soft-locked, or journaled volumes unless allowed by `force` rules;
- opens extents and catalog B-trees, optionally opens the attributes B-tree, installs xattr handlers, and loads the allocation file inode;
- loads root inode, sets default HFS+ dentry ops, and creates `sb->s_root`;
- finds or creates the hidden directory used for hard-link/private file handling;
- on writable mounts, prepares/commits the volume header and initializes security on a newly created hidden directory when supported;
- unwinds all allocated/opened resources on failure.

## Super Operations and Reconfigure

- `hfsplus_sops` wires inode allocation/free, writeback, eviction, put_super, sync, statfs, and show_options.
- `hfsplus_put_super()` cancels delayed sync, marks writable volumes cleanly unmounted and not inconsistent, syncs, drops metadata inodes/B-trees, frees header buffers, and leaves `sbi` for RCU-delayed free.
- `hfsplus_statfs()` reports HFS+ magic, block size/count/free count, a synthetic file count, free CNIDs, fsid, and maximum name length.
- `hfsplus_reconfigure()` syncs before remount and blocks read-write transition for unclean, locked, or journaled volumes unless `force` permits the journaled/locked checks.

## Module and Cache Lifecycle

- `hfsplus_init_fs_context()` allocates and initializes `hfsplus_sb_info`, fills defaults for initial mounts, and installs `hfsplus_context_ops`.
- `hfsplus_get_tree()` mounts via `get_tree_bdev()`.
- `hfsplus_free_fc()` frees unmounted context state.
- `hfsplus_kill_super()` calls `kill_block_super()` and schedules `sbi` for RCU-delayed cleanup.
- `init_hfsplus_fs()` creates the inode cache, creates the attributes-tree cache, and registers the filesystem.
- `exit_hfsplus_fs()` unregisters the filesystem, waits for RCU, destroys the attributes cache, and destroys the inode cache.

## Dependencies

Uses Linux module/init, VFS, block-device, page-cache, fs_context, NLS, slab, xattr, HFS+ B-tree/catalog/extent/allocation helpers, and wrapper volume-header I/O.

## Research Notes

This file coordinates the filesystem-wide dirty state: special metadata files are ordinary inodes for writeback, but HFS+ must explicitly write the B-tree/allocation mappings and commit the volume header to keep on-disk state consistent. The mount path is conservative for journaled or unclean volumes because this driver does not replay HFS+ journals.
