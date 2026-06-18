# File Research: sources/os/linux/linux/fs/f2fs/inode.c

Read completely: 1066 lines.

## Summary
Implements F2FS inode loading, validation, flag restoration, checksum calculation, inode writeback, eviction, failed-new-inode cleanup, and VFS operation assignment. It translates on-disk `struct f2fs_inode` fields into `struct inode` and `struct f2fs_inode_info`, then writes in-memory state back to inode node pages.

## Main Responsibilities
- Marks inodes dirty using F2FS dirty-inode policy.
- Maps F2FS inode flags to VFS inode flags.
- Encodes and decodes special-file device numbers.
- Computes, verifies, and sets inode checksums.
- Validates on-disk inode metadata, feature dependencies, inline state, compression state, xattr state, project quota state, and device-alias state.
- Reads inode fields and initializes extent caches/stat counters.
- Instantiates inode operation tables for regular files, directories, symlinks, special files, and meta inodes.
- Writes inode state back to node folios.
- Evicts inodes, truncates deleted inode data, drops quotas/extents/compression cache, and removes inode node pages.
- Handles failed inode creation by syncing, orphaning, or freeing the NID.

## Key APIs
- Dirty/flags: `f2fs_mark_inode_dirty_sync()`, `f2fs_set_inode_flags()`.
- Checksum: `f2fs_inode_chksum_verify()`, `f2fs_inode_chksum_set()`.
- Load: `f2fs_iget()`, `f2fs_iget_retry()`, `do_read_inode()`.
- Writeback: `f2fs_update_inode()`, `f2fs_update_inode_page()`, `f2fs_write_inode()`.
- Eviction/failure: `f2fs_evict_inode()`, `f2fs_handle_failed_inode()`, `f2fs_remove_donate_inode()`.

## Important Behavior
`do_read_inode()` reads the inode node folio, populates mode, uid/gid, nlink, size, block count, timestamps, generation, depth or GC failures, xattr nid, flags, advice, parent inode, directory level, inline flags, extra-attribute size, inline-xattr size, project id, creation time, compression fields, extent cache state, and stats.

`sanity_check_inode()` rejects corrupted or unsupported combinations: zero block count, mismatched inode footer ino/nid, self-referential xattr nid, directory nlink of one, invalid extra-attr size, compression inconsistency, invalid inline-xattr size, feature flags without extra-attr support, invalid inline data/dentry state, casefold without feature support, invalid xattr nid range, and device-alias without feature or pin flag.

`f2fs_iget()` forbids exposing meta inodes through ordinary iget hits, assigns address-space operations for node/meta/compress inodes, and assigns file/dir/symlink/special inode operations for normal inodes.

`f2fs_update_inode()` serializes current in-memory inode state into the raw inode, including read extent, inline flags, timestamps, depth/GC failures, xattr nid, flags, project id, creation time, compression metadata, rdev encoding, and checksum. Atomic files avoid writing size except after atomic commit.

`f2fs_write_inode()` skips meta inodes, avoids unnecessary lazytime-only updates, returns `-EIO` on checkpoint error, re-dirties when checkpoint is not ready, updates the inode page, and balances the filesystem when called with writeback pressure.

`f2fs_evict_inode()` aborts atomic writes, releases COW inodes, drops page cache, invalidates compression cache, removes dirty/donate state, destroys extents, truncates deleted inode data, removes inode node pages, repairs dirty state on failure, drops quota, updates stats, invalidates node/xattr pages, and restores append/update inode tracking for still-linked inodes.

Failed inode creation clears nlink, writes/syncs the inode page, unlocks the new inode, then either adds it to the orphan list or marks its NID free depending on NAT state.

## State and Synchronization
Uses inode node folios, node writeback waits, extent-tree locks, inode dirty flags, quota initialization/drop, orphan inode tracking, checkpoint state, compression counters, donate inode lists, COW inode references, and freeze protection during deletion.

## Risks
Inode loading is a trust boundary for on-disk metadata. Missing a feature dependency or corrupted field can later corrupt block accounting, xattr lookup, compression state, or directory behavior. Eviction must handle many partially failed states without leaving dirty inode-list entries or leaked orphan/NID state. Atomic-write and COW inode lifetimes are especially sensitive because inode size and dirty state have special commit rules.
